# tgGPT

A telegram bot for ChatGPT API.

![output_accelerated](https://user-images.githubusercontent.com/70903329/232048571-db6eb660-b5f0-4e82-91ea-7b4474d4791a.gif)


## Feature
- Streaming by edit message
- Chat mode
- Q&A mode
- Select model
- Retry
- Edit query
- Check out API usage

## Usage

1. Create your own telegram-bot by [@BotFather](https://t.me/BotFather) and get HTTP API.
2. Clone this repo.
```sh
git clone https://github.com/MZhao-ouo/tgGPT.git
```
3. Edit `config.json`
```sh
cp config_example.json config.json
```
Enter your bot HTTP API, OpenAi API KEY, and whitelist.

You can find your telegram id by [@JsonDumpBot](https://t.me/JsonDumpBot). ("message" > "from" > "id" )

4. Install python library
```sh
pip install requirements.txt
```

5. Run
```sh
python tgGPT.py
```
