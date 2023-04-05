from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

accomplished_btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("重试", callback_data="retry_button"),
            ]
        ]
    )

retry_btn_all = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("<", callback_data="last_button"),
            InlineKeyboardButton("重试", callback_data="retry_button"),
            InlineKeyboardButton(">", callback_data="next_button")
        ]
    ]
)

retry_btn_start = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("重试", callback_data="retry_button"),
            InlineKeyboardButton(">", callback_data="next_button")
        ]
    ]
)

retry_btn_end = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("<", callback_data="last_button"),
            InlineKeyboardButton("重试", callback_data="retry_button"),
        ]
    ]
)

random_text = ["你好呀！", "我是一个机器人。", "我很勇敢哦", "好啦", "你超勇的嘛", "Design by MZhao", "你可以先体验一下"]
