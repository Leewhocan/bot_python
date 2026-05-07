import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.states import FeedbackState
from database.db import save_feedback
from config import ADMIN_ID

router = Router()

def _user_display(user) -> str:
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    else:
        return f"ID{user.id}"

@router.message(FeedbackState.waiting_message)
async def process_feedback(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or " "
    text = message.text

    await save_feedback(user_id, username, text)
    await message.answer("💚 Спасибо за ваш отзыв! Он поможет стать нам лучше.")
    await state.clear()

    # Уведомление админу
    user_display = _user_display(message.from_user)
    try:
        await message.bot.send_message(
            ADMIN_ID,
            f"📝 <b>Новый отзыв!</b>\nОт: {user_display}\nСообщение: {text}"
        )
    except Exception as e:
        logging.warning(f"Не удалось уведомить админа о новом отзыве: {e}")