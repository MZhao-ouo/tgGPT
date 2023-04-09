import requests, json

class OpenAIClient():
    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.chat_url = "https://api.openai.com/v1/chat/completions"
        self.billing_url = "https://api.openai.com/v1/billing"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.model = "gpt-3.5-turbo"
        self.temperature = 1
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        self.mode = "chat"  # "chat" or "qa"

    def get_chat_response(self):
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": 1,
            "stream": True,
            "messages": self.messages
        }
        return requests.post(self.chat_url, headers=self.headers, json=payload, stream=True)

    def get_billing_data(self):
        response = requests.get(self.billing_url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")


# Some Functions
def decode_chat_response(response):
    for chunk in response.iter_lines():
        if chunk:
            chunk = chunk.decode()
            chunk_length = len(chunk)
            try:
                chunk = json.loads(chunk[6:])
            except json.JSONDecodeError:
                print(f"JSON解析错误,收到的内容: {chunk}")
                continue
            if chunk_length > 6 and "delta" in chunk["choices"][0]:
                if chunk["choices"][0]["finish_reason"] == "stop":
                    break
                try:
                    yield chunk["choices"][0]["delta"]["content"]
                except Exception as e:
                    # logging.error(f"Error: {e}")
                    continue
