import logging, json
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from openai_func import OpenAIClient
from preset import *
from utils import get_reply_chunks

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    new(update, context)
    
    await context.bot.send_message(chat_id=chat_id, text="欢迎使用tgGPT！", reply_markup=None)
    

async def new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    del lastest_message_id[chat_id]
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="新建对话成功！")
    
    
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    if chat_id not in ai_clients:
        ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    if chat_id in lastest_message_id:
        await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=lastest_message_id[chat_id], reply_markup=None)
    if chat_id in config["whitelist"]:
        flag = True
    else:
        flag = False

    ai_clients[chat_id].messages.append({"role": "user", "content": update.message.text})
    logging.info(f"User: {update.message.text}")
    
    reply = await context.bot.send_message(chat_id=chat_id, text="生成中......")
    reply_id = reply.message_id
    lastest_message_id[chat_id] = reply_id
    
    reply_text = ""
    reply_chunks = get_reply_chunks(ai_clients[chat_id], flag)
    index = 0
    for chunk in reply_chunks:
        index += 1
        reply_text += chunk
        if index % 16 == 0:
            await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id)
    if index % 16 != 0:
        await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id)
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=reply_id, reply_markup=accomplished_btn)
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    retry_replies[chat_id] = [reply_text]
    retry_index[chat_id] = 0
    logging.info(f"Reply: {reply_text}")
    
    
async def retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    if chat_id in config["whitelist"]:
        flag = True
    else:
        flag = False
    reply_id = update.callback_query.message.message_id
    ai_clients[chat_id].messages.pop()
    
    reply_text = ""
    await context.bot.edit_message_text("重试中......", chat_id=chat_id, message_id=reply_id)
    reply_chunks = get_reply_chunks(ai_clients[chat_id], flag)
    index = 0
    for chunk in reply_chunks:
        index += 1
        reply_text += chunk
        if index % 16 == 0:
            await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id)
    if index % 16 != 0:
        await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id)
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=reply_id, reply_markup=retry_btn_end)
    
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
    

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    query = update.callback_query
    if query.data == "retry_button":
        await retry(update, context)
    if query.data == "last_button":
        await last_reply(update, context)
    if query.data == "next_button":
        await next_reply(update, context)
    if query.data == "empty":
        pass

async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

if __name__ == '__main__':
    with open('config.json', 'r', encoding="utf-8") as f:
        config = json.load(f)
    
    ai_clients = {}
    lastest_message_id = {}
    retry_replies = {}
    retry_index = {}
    
    application = ApplicationBuilder().token(config["bot_token"]).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('new', new))
    application.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, empty))
    application.add_handler(MessageHandler(filters.TEXT, chat))
    application.add_handler(CallbackQueryHandler(button))    
    
    application.run_polling()
