import logging, json, asyncio
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from openai_func import OpenAIClient, get_usage
from preset import *
from utils import clean_markup, edit_reply

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    await new_chat(update, context)
    await context.bot.set_my_commands(cmds_list)
    
    await context.bot.send_message(chat_id=chat_id, text="欢迎使用tgGPT！", reply_markup=None)
    

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    ai_clients[chat_id].mode = "chat"
    await clean_markup(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="新建对话成功！")
    
    
async def new_qa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    ai_clients[chat_id].mode = "qa"
    await clean_markup(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="已切换至问答模式（单次对话）！", reply_markup=None)


async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    if chat_id not in ai_clients:
        ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    delete_cmd_task = asyncio.create_task(context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id))
    total_usage, start_date, end_date = get_usage(ai_clients[chat_id])
    usage_text = f"{start_date}~{end_date}：\n```{total_usage}$```"
    usage_reply_task = asyncio.create_task(context.bot.send_message(chat_id=chat_id, text=usage_text, parse_mode="Markdown"))
    await asyncio.gather(delete_cmd_task, usage_reply_task)
    

async def set_system_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    if chat_id not in ai_clients:
        ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    ai_clients[chat_id].messages[0] = {"role": "system", "content": update.message.text}
    
    
async def qa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    lastest_user_msg_id[chat_id] = update.message.message_id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    ai_clients[chat_id].messages = [ai_clients[chat_id].messages[0], {"role": "user", "content": update.message.text}]
    logging.info(f"User: {update.message.text}")
    
    clean_markup_task = asyncio.create_task(clean_markup(update, context))
    send_message_task = asyncio.create_task(context.bot.send_message(chat_id=chat_id, text="生成中......"))
    await asyncio.gather(clean_markup_task, send_message_task)
    
    reply_id = send_message_task.result().message_id
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, qa_acc_btn)
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    retry_replies[chat_id] = [reply_text]
    retry_index[chat_id] = 0
    logging.info(f"Reply: {reply_text}")
    
    
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    lastest_user_msg_id[chat_id] = update.message.message_id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    ai_clients[chat_id].messages.append({"role": "user", "content": update.message.text})
    logging.info(f"User: {update.message.text}")
    
    clean_markup_task = asyncio.create_task(clean_markup(update, context))
    send_message_task = asyncio.create_task(context.bot.send_message(chat_id=chat_id, text="生成中......"))
    await asyncio.gather(clean_markup_task, send_message_task)
    
    reply_id = send_message_task.result().message_id
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, chat_acc_btn)
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    retry_replies[chat_id] = [reply_text]
    retry_index[chat_id] = 0
    logging.info(f"Reply: {reply_text}")


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    editted_msg = update.edited_message
    if lastest_user_msg_id[chat_id] is None or editted_msg.id != lastest_user_msg_id[chat_id]:
        return

    reply_id = editted_msg.message_id + 1
    ai_clients[chat_id].messages = ai_clients[chat_id].messages[:-2]
    ai_clients[chat_id].messages.append({"role": "user", "content": editted_msg.text})
    
    await context.bot.edit_message_text("生成中......", chat_id=chat_id, message_id=reply_id)
    
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, chat_acc_btn)
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    retry_replies[chat_id] = [reply_text]
    retry_index[chat_id] = 0
    logging.info(f"Reply: {reply_text}")
    
    
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    query = update.callback_query
    try:
        if query.data == "retry_button":
            await retry(update, context)
        if query.data == "last_button":
            await last_reply(update, context)
        if query.data == "next_button":
            await next_reply(update, context)
        if query.data == "new":
            await new_chat(update, context)
        if query.data == "empty":
            pass
    except:
        logging.debug("Button error")
        await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=query.message.message_id, reply_markup=None)
    

async def retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    reply_id = update.callback_query.message.message_id
    if lastest_user_msg_id[chat_id] is None or update.callback_query.message.id != lastest_user_msg_id[chat_id] + 1:
        return
        
    await context.bot.edit_message_text("重试中......", chat_id=chat_id, message_id=reply_id)

    ai_clients[chat_id].messages.pop()
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, retry_btn_end)
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    retry_replies[chat_id].append(reply_text)
    retry_index[chat_id] = len(retry_replies[chat_id]) - 1
    logging.info(f"Retry reply: {reply_text}")
    

async def last_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    reply_id = update.callback_query.message.message_id
    retry_index[chat_id] -= 1
    
    if retry_index[chat_id] == 0:
        reply_btn = retry_btn_start
    else:
        reply_btn = retry_btn_all
        
    last_reply_text = retry_replies[chat_id][retry_index[chat_id]]
    ai_clients[chat_id].messages[-1]["content"] = last_reply_text
    await context.bot.edit_message_text(last_reply_text, chat_id=chat_id, message_id=reply_id, reply_markup=reply_btn)
    
    
async def next_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    reply_id = update.callback_query.message.message_id
    retry_index[chat_id] += 1
    
    if retry_index[chat_id] == len(retry_replies[chat_id]) - 1:
        reply_btn = retry_btn_end
    else:
        reply_btn = retry_btn_all
    
    next_reply_text = retry_replies[chat_id][retry_index[chat_id]]
    ai_clients[chat_id].messages[-1]["content"] = next_reply_text
    await context.bot.edit_message_text(next_reply_text, chat_id=chat_id, message_id=reply_id, reply_markup=reply_btn)


async def response_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    if chat_id not in ai_clients:
        ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
        
    if ai_clients[chat_id].mode == "qa":
        await qa(update, context)
    elif ai_clients[chat_id].mode == "chat":
        await chat(update, context)
        

async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

async def update_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    total_usage, start_date, end_date = get_usage(ai_clients[chat_id])
    cmds_list[3] = BotCommand("usage", f"{round(total_usage, 4)}$")
    await context.bot.set_my_commands(cmds_list)

if __name__ == '__main__':    
    application = ApplicationBuilder().token(config["bot_token"]).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('new_chat', new_chat))
    application.add_handler(CommandHandler('new_qa', new_qa))
    usage_handler = CommandHandler('usage', usage)
    usage_handler.callback = update_usage
    application.add_handler(usage_handler)
    application.add_handler(CommandHandler('system_prompt', set_system_prompt))
    application.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edit))
    application.add_handler(MessageHandler(filters.TEXT, response_text))
    application.add_handler(CallbackQueryHandler(button))
    
    application.run_polling()
