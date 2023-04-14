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
    await context.bot.send_message(chat_id=chat_id, text="欢迎使用tgGPT！", reply_markup=None)
    await new_chat(update, context)
    await context.bot.set_my_commands(cmds_list)
    

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    ai_clients[chat_id].mode = "chat"
    await clean_markup(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"新建对话💬当前模型: {ai_clients[chat_id].model}", reply_markup=models_btn)
    
    
async def new_qa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    ai_clients[chat_id].mode = "qa"
    await clean_markup(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"单次问答🚀当前模型: {ai_clients[chat_id].model}", reply_markup=models_btn)


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
    edit_message_id= None
    try:
        system_prompt = " ".join(update.message.text.split(" ")[1:])
    except:
        system_prompt = " ".join(update.edited_message.text.split(" ")[1:])
        edit_message_id = update.edited_message.message_id + 1
    if system_prompt == "":
        reply_text = f"当前System Prompt: \n`{ai_clients[chat_id].messages[0]['content']}`\n如需更换System Prompt，请使用`/set_system_prompt <system_prompt>`"
    else:
        ai_clients[chat_id].messages[0] = {"role": "system", "content": system_prompt}
        reply_text = f"System Prompt已设置为：\n`{system_prompt}`"
    if edit_message_id is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text, parse_mode="Markdown", reply_to_message_id=update.message.message_id)
    else:
        await context.bot.edit_message_text(reply_text, chat_id=update.effective_chat.id, message_id= edit_message_id, parse_mode="Markdown")

    
    
async def qa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    lastest_user_msg_id[chat_id] = update.message.message_id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    ai_clients[chat_id].messages = [ai_clients[chat_id].messages[0], {"role": "user", "content": update.message.text}]
    logging.info(f"User: {update.message.text}")
    
    clean_markup_task = asyncio.create_task(clean_markup(update, context))
    send_message_task = asyncio.create_task(context.bot.send_message(chat_id=chat_id, text="生成中……", reply_to_message_id=update.message.message_id))
    await asyncio.gather(clean_markup_task, send_message_task)
    
    reply_id = send_message_task.result().message_id
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, get_acc_btn(ai_clients[chat_id].mode))
    
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
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, get_acc_btn(ai_clients[chat_id].mode))
    
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
    ai_clients[chat_id].messages = ai_clients[chat_id].messages[:-2] + [{"role": "user", "content": editted_msg.text}]
    
    await context.bot.edit_message_text("生成中......", chat_id=chat_id, message_id=reply_id)
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, get_acc_btn(ai_clients[chat_id].mode))
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    retry_replies[chat_id] = [reply_text]
    retry_index[chat_id] = 0
    logging.info(f"Reply: {reply_text}")
    
    
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    query = update.callback_query
    logging.info(f"Button: {query.data}")
    try:
        if query.data == "retry_button":
            await retry(update, context)
        elif query.data == "last_button":
            await last_reply(update, context)
        elif query.data == "next_button":
            await next_reply(update, context)
        elif query.data == "new":
            await new_chat(update, context)
        elif query.data == "qa2chat":
            await qa2chat(update, context)
        elif query.data in ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-4", "gpt-4-0314"]:
            await change_model(update, context)
        elif query.data == "empty":
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
    reply_text = await edit_reply(ai_clients[chat_id], context, chat_id, reply_id, get_retry_btn_end(ai_clients[chat_id].mode))
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    retry_replies[chat_id].append(reply_text)
    retry_index[chat_id] = len(retry_replies[chat_id]) - 1
    logging.info(f"Retry reply: {reply_text}")
    

async def last_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    reply_id = update.callback_query.message.message_id
    retry_index[chat_id] -= 1
    
    if retry_index[chat_id] == 0:
        reply_btn = get_retry_btn_start(ai_clients[chat_id].mode)
    else:
        reply_btn = get_retry_btn_all(ai_clients[chat_id].mode)
        
    last_reply_text = retry_replies[chat_id][retry_index[chat_id]]
    ai_clients[chat_id].messages[-1]["content"] = last_reply_text
    await context.bot.edit_message_text(last_reply_text, chat_id=chat_id, message_id=reply_id, reply_markup=reply_btn)
    
    
async def next_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    reply_id = update.callback_query.message.message_id
    retry_index[chat_id] += 1
    
    if retry_index[chat_id] == len(retry_replies[chat_id]) - 1:
        reply_btn = get_retry_btn_end(ai_clients[chat_id].mode)
    else:
        reply_btn = get_retry_btn_all(ai_clients[chat_id].mode)
    
    next_reply_text = retry_replies[chat_id][retry_index[chat_id]]
    ai_clients[chat_id].messages[-1]["content"] = next_reply_text
    await context.bot.edit_message_text(next_reply_text, chat_id=chat_id, message_id=reply_id, reply_markup=reply_btn)
    

async def qa2chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    ai_clients[chat_id].mode = "chat"
    await context.bot.send_message(chat_id=chat_id, text="已切换到Chat模式，可继续对话。")
    await clean_markup(update, context)


async def response_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    if chat_id not in ai_clients:
        ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    if ai_clients[chat_id].mode == "qa":
        await qa(update, context)
    elif ai_clients[chat_id].mode == "chat":
        await chat(update, context)
    await update_usage(update, context)
    
async def change_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    query = update.callback_query
    if ai_clients[chat_id].model == query.data:
        return
    ai_clients[chat_id].model = query.data
    # await context.bot.send_message(chat_id=chat_id, text=f"已切换至{ai_clients[chat_id].model}模型", reply_markup=None)
    original_text = query.message.text[:11]
    await context.bot.edit_message_text(original_text+ai_clients[chat_id].model, chat_id, query.message.message_id, reply_markup=models_btn)
        

async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

async def update_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    total_usage = get_usage(ai_clients[chat_id])[0]
    cmds_list[3] = BotCommand("usage", f"{round(total_usage, 4)}$")
    await context.bot.set_my_commands(cmds_list)

if __name__ == '__main__':    
    application = ApplicationBuilder().token(config["bot_token"]).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('new_chat', new_chat))
    application.add_handler(CommandHandler('new_qa', new_qa))
    application.add_handler(CommandHandler('usage', usage))
    application.add_handler(CommandHandler('sys_prompt', set_system_prompt))
    
    application.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edit))
    application.add_handler(MessageHandler(filters.TEXT, response_text))
    
    
    application.add_handler(CallbackQueryHandler(button))
    
    application.run_polling()
