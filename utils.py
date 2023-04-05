from openai_func import OpenAIClient, decode_chat_response
from preset import random_text
import random

def get_reply_chunks(client: OpenAIClient, flag: bool):
    if flag:
        response = client.get_chat_response()
        response_contents = decode_chat_response(response)
    else:
        index = random.randint(0, len(random_text) - 1)
        response_contents = iter([random_text[index]])
    
    return response_contents
