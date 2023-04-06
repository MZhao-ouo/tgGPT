from openai_func import OpenAIClient, decode_chat_response
from preset import random_text, config
from telegram import Update
from telegram.ext import ContextTypes
import random, logging

def get_reply_chunks(client: OpenAIClient, flag: bool):
    if flag:
        response = client.get_chat_response()
        response_contents = decode_chat_response(response)
    else:
        index = random.randint(0, len(random_text) - 1)
        response_contents = iter([random_text[index]])
    
    return response_contents


async def clean_markup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    current_msg_id = update.message.message_id
    for i in range(1, 4):
        try:
            await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=current_msg_id-i, reply_markup=None)
        except Exception as e:
            logging.debug(e)
            pass
    

async def edit_reply(client: OpenAIClient, context: ContextTypes.DEFAULT_TYPE, chat_id: int, reply_id: int, reply_markup):
    if chat_id in config["whitelist"]:
        flag = True
    else:
        flag = False
    reply_text = ""
    reply_chunks = get_reply_chunks(client, flag)
    index = 0
    for chunk in reply_chunks:
        index += 1
        reply_text += chunk
        if index % 16 == 0:
            await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id)
    if index % 16 != 0:
        await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id, parse_mode="Markdown")
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=reply_id, reply_markup=reply_markup)
    
    return reply_text
