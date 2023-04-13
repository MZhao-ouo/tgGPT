from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
import json

with open('config.json', 'r', encoding="utf-8") as f:
    config = json.load(f)

ai_clients = {}
lastest_user_msg_id = {}
retry_replies = {}
retry_index = {}

cmds_list = [
    BotCommand("start", "重置"),
    BotCommand("new_chat", "新建聊天"),
    BotCommand("new_qa", "新建问答"),
    BotCommand("usage", "查看用量"),
    BotCommand("system_prompt", "设置系统提示")
]

retry_btn = InlineKeyboardButton("🔁 重试", callback_data="retry_button")
new_chat_btn = InlineKeyboardButton("🧹 新对话", callback_data="new_chat")
qa2chat_btn = InlineKeyboardButton("🤖 转为对话", callback_data="qa2chat")
last_btn = InlineKeyboardButton("⬅️", callback_data="last_button")
next_btn = InlineKeyboardButton("➡️", callback_data="next_button")
isbegin_btn = InlineKeyboardButton("已至开头", callback_data="empty")
isend_btn = InlineKeyboardButton("已至末尾", callback_data="empty")

chat_acc_btn = InlineKeyboardMarkup([
    [ retry_btn, new_chat_btn ]
])

qa_acc_btn = InlineKeyboardMarkup([
    [ retry_btn, qa2chat_btn ]
])

retry_btn_all = InlineKeyboardMarkup([
    [ last_btn, next_btn ],
    [ retry_btn, new_chat_btn ]
])

retry_btn_start = InlineKeyboardMarkup([
    [ isbegin_btn, next_btn ],
    [ retry_btn, new_chat_btn ]
])

retry_btn_end = InlineKeyboardMarkup([
    [ last_btn,  isend_btn ],
    [ retry_btn, new_chat_btn ]
])

random_text = ["你好呀！", "我是一个机器人。", "我很勇敢哦", "好啦", "你超勇的嘛", "Design by MZhao", "你可以先体验一下"]
