import requests, json, datetime

class OpenAIClient():
    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.chat_url = "https://api.openai.com/v1/chat/completions"
        self.usage_url = "https://api.openai.com/dashboard/billing/usage"
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

    def get_billing_data(self, suffix_url=""):
        response = requests.get(self.usage_url+suffix_url, headers=self.headers)
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

def get_usage(ai_client: OpenAIClient, start_date=None, end_date=None):
    # date的格式是YYYY-MM-DD
    today = datetime.datetime.now()
    if start_date is None and end_date is None:
        end_date = today.replace(month=today.month+1).strftime("%Y-%m-%d")
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
    elif start_date is None:
        start_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    elif end_date is None:
        end_date = today.strftime("%Y-%m-%d")
        
    suffix_url = f"?start_date={start_date}&end_date={end_date}"
    billing_data = ai_client.get_billing_data(suffix_url)
    total_usage = billing_data['total_usage'] / 100
    
    return  total_usage, start_date, end_date
