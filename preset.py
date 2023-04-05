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
