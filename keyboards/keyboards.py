from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать викторину", callback_data="start_quiz")]
    ])

def get_answer_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for idx, option_text in enumerate(options):
        buttons.append([InlineKeyboardButton(
            text=f"{idx+1}. {option_text}",
            callback_data=f"answer_{idx}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_result_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться результатом", callback_data="share")],
        [InlineKeyboardButton(text="📞 Связаться с сотрудником", callback_data="contact")],
        [InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="feedback")],
        [InlineKeyboardButton(text="🔄 Попробовать ещё раз", callback_data="restart")]
    ])

def get_share_keyboard(bot_username: str, animal: str):
    share_text = f"🦁 Моё тотемное животное — {animal}! Узнай своего: https://t.me/{bot_username}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Копировать ссылку", switch_inline_query=share_text)]
    ])

def get_contact_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, отправить результат", callback_data="send_contact")],
        [InlineKeyboardButton(text="❌ Нет, спасибо", callback_data="no_contact")]
    ])

def get_restart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart")]
    ])

def get_main_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔄 Попробовать ещё раз")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )