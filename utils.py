from openai_func import OpenAIClient, decode_chat_response

def get_reply_chunks(client: OpenAIClient):
    response = client.get_chat_response()
    response_contents = decode_chat_response(response)
    
    return response_contents
