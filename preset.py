from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import json

with open('config.json', 'r', encoding="utf-8") as f:
    config = json.load(f)

ai_clients = {}
lastest_user_msg_id = {}
retry_replies = {}
retry_index = {}

accomplished_btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔁 重试", callback_data="retry_button"),
                InlineKeyboardButton("🧹 新对话", callback_data="new")
            ]
        ]
    )

retry_btn_all = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️", callback_data="last_button"),
            InlineKeyboardButton("➡️", callback_data="next_button")
        ],
        [
            InlineKeyboardButton("🔁 重试", callback_data="retry_button"),
            InlineKeyboardButton("🧹 新对话", callback_data="new")
        ]
    ]
)

retry_btn_start = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("已至开头", callback_data="empty"),
            InlineKeyboardButton("➡️", callback_data="next_button")
        ],
        [
            InlineKeyboardButton("🔁 重试", callback_data="retry_button"),
            InlineKeyboardButton("🧹 新对话", callback_data="new")
        ]
    ]
)

retry_btn_end = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️", callback_data="last_button"),
            InlineKeyboardButton("已至末尾", callback_data="empty"),
        ],
        [
            InlineKeyboardButton("🔁 重试", callback_data="retry_button"),
            InlineKeyboardButton("🧹 新对话", callback_data="new")
        ]
    ]
)

random_text = ["你好呀！", "我是一个机器人。", "我很勇敢哦", "好啦", "你超勇的嘛", "Design by MZhao", "你可以先体验一下"]
