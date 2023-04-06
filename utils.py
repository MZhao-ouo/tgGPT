from openai_func import OpenAIClient, decode_chat_response
from preset import random_text
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
    

