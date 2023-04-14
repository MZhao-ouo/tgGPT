from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
import json

with open('config.json', 'r', encoding="utf-8") as f:
    config = json.load(f)

ai_clients = {}
lastest_user_msg_id = {}
retry_replies = {}
retry_index = {}

cmds_list = [
    BotCommand("start", "🔁重置"),
    BotCommand("new_chat", "💬新建对话（可选model）"),
    BotCommand("new_qa", "🚀新建问答（可选model）"),
    BotCommand("usage", "🔋查看用量"),
    BotCommand("sys_prompt", "🤖设置系统提示"),
]

retry_btn = InlineKeyboardButton("🔁 重试", callback_data="retry_button")
new_chat_btn = InlineKeyboardButton("🧹 新对话", callback_data="new_chat")
qa2chat_btn = InlineKeyboardButton("🤖 转为对话", callback_data="qa2chat")
last_btn = InlineKeyboardButton("⬅️", callback_data="last_button")
next_btn = InlineKeyboardButton("➡️", callback_data="next_button")
isbegin_btn = InlineKeyboardButton("已至开头", callback_data="empty")
isend_btn = InlineKeyboardButton("已至末尾", callback_data="empty")


def get_acc_btn(cli_mode):
    if cli_mode == "chat":
        return InlineKeyboardMarkup([
            [ retry_btn, new_chat_btn ]
        ])
    elif cli_mode == "qa":
        return InlineKeyboardMarkup([
            [ retry_btn, qa2chat_btn ]
        ])
    else:
        return None

def get_retry_btn_all(cli_mode):
    if cli_mode == "chat":
        return InlineKeyboardMarkup([
            [ last_btn, next_btn ],
            [ retry_btn, new_chat_btn ]
        ])
    elif cli_mode == "qa":
        return InlineKeyboardMarkup([
            [ last_btn, next_btn ],
            [ retry_btn, qa2chat_btn ]
        ])
    else:
        return None
    
def get_retry_btn_start(cli_mode):
    if cli_mode == "chat":
        return InlineKeyboardMarkup([
            [ isbegin_btn, next_btn ],
            [ retry_btn, new_chat_btn ]
        ])
    elif cli_mode == "qa":
        return InlineKeyboardMarkup([
            [ isbegin_btn, next_btn ],
            [ retry_btn, qa2chat_btn ]
        ])
    else:
        return None

def get_retry_btn_end(cli_mode):
    if cli_mode == "chat":
        return InlineKeyboardMarkup([
            [ last_btn,  isend_btn ],
            [ retry_btn, new_chat_btn ]
        ])
    elif cli_mode == "qa":
        return InlineKeyboardMarkup([
            [ last_btn,  isend_btn ],
            [ retry_btn, qa2chat_btn ]
        ])
    else:
        return None
    
models_btn = InlineKeyboardMarkup([
    [ InlineKeyboardButton("🤖 gpt-3.5-turbo", callback_data="gpt-3.5-turbo") ],
    [ InlineKeyboardButton("🤖 gpt-4", callback_data="gpt-4") ],
])

random_text = ["你好呀！", "我是一个机器人。", "我很勇敢哦", "好啦", "你超勇的嘛", "Design by MZhao", "你可以先体验一下"]
