import logging, json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai_func import OpenAIClient
from utils import get_reply_chunks

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="新建对话成功！")
    
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    if chat_id not in ai_clients:
        ai_clients[chat_id] = OpenAIClient(config["openai_api_key"])

    ai_clients[chat_id].messages.append({"role": "user", "content": update.message.text})
    logging.info(f"User: {update.message.text}")
        
    reply = await context.bot.send_message(chat_id=chat_id, text="生成中...")
    reply_id = reply.message_id    
    
    reply_text = ""
    reply_chunks = get_reply_chunks(ai_clients[chat_id])
    index = 0
    for chunk in reply_chunks:
        index += 1
        reply_text += chunk
        if index % 8 == 0:
            await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id)
    if index % 8 != 0:
        await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id)
    
    ai_clients[chat_id].messages.append({"role": "assistant", "content": reply_text})
    logging.info(f"Reply: {reply_text}")

if __name__ == '__main__':
    with open('config.json', 'r', encoding="utf-8") as f:
        config = json.load(f)
    ai_clients = {}
    
    application = ApplicationBuilder().token(config["bot_token"]).build()
    
    start_handler = CommandHandler('start', new)
    application.add_handler(start_handler)
    new_handler = CommandHandler('new', new)
    application.add_handler(new_handler)
    
    msg_handler = MessageHandler(filters.TEXT, chat)
    application.add_handler(msg_handler)
    
    
    application.run_polling()
