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
    edit_value = 4
    for chunk in reply_chunks:
        index += 1
        reply_text += chunk
        if index % edit_value == 0:
            md_end = ""
            # if reply_text.count("```") % 2 == 1:
            #     md_end = "\n```\n"
            await context.bot.edit_message_text(reply_text + md_end, chat_id=chat_id, message_id=reply_id)
            edit_value = min(edit_value * 2, 18)
    try:
        await context.bot.edit_message_text(reply_text, chat_id=chat_id, message_id=reply_id, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        logging.debug(e)
        pass
    
    return reply_text
