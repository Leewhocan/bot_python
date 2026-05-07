import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.keyboards import get_share_keyboard, get_contact_keyboard, get_start_keyboard
from states.states import ContactState, FeedbackState
from config import ADMIN_ID, STAFF_IDS

router = Router()

def _user_display(user: types.User) -> str:
    """Возвращает строковое представление пользователя: @username, имя или ID."""
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    else:
        return f"ID{user.id}"

@router.callback_query(F.data == "share")
async def share_result(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    animal = data.get("animal")
    if not animal:
        await callback.answer("Результат не найден. Начните викторину заново.", show_alert=True)
        return
    bot_username = (await callback.bot.me()).username
    await callback.message.answer(
        "📣 Нажми кнопку ниже, чтобы скопировать текст и поделиться своей находкой в соцсетях!",
        reply_markup=get_share_keyboard(bot_username, animal)
    )
    await callback.answer()

@router.callback_query(F.data == "contact")
async def contact_request(callback: CallbackQuery, state: FSMContext):
    contact_text = (
        f"📞 Хотите отправить результат вашей викторины сотруднику зоопарка для более быстрой консультации?"
    )
    await callback.message.answer(contact_text, reply_markup=get_contact_keyboard())
    await state.set_state(ContactState.waiting_confirm)
    await callback.answer()

@router.callback_query(F.data == "send_contact", ContactState.waiting_confirm)
async def send_contact(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    animal = data.get("animal")
    
    if not animal:
        await callback.answer("Результат уже недоступен. Пройдите викторину заново.", show_alert=True)
        await callback.message.answer("Пожалуйста, начните викторину сначала /start")
        await state.clear()
        return

    user_info = _user_display(callback.from_user)
    result_text = (
        f"📩 <b>Запрос на обратную связь</b>\n"
        f"Результат викторины: <b>{animal}</b>\n"
        f"Пользователь: {user_info}"
    )

    # Отправляем сотрудникам
    for staff_id in STAFF_IDS:
        try:
            await callback.bot.send_message(staff_id, result_text)
        except Exception as e:
            logging.warning(f"Не удалось отправить заявку сотруднику {staff_id}: {e}")

    # Если админ не в списке сотрудников – тоже уведомляем
    if ADMIN_ID not in STAFF_IDS:
        try:
            await callback.bot.send_message(ADMIN_ID, result_text)
        except Exception as e:
            logging.warning(f"Не удалось уведомить админа: {e}")

    await callback.message.answer(
        "✅ Спасибо! Ваш запрос отправлен сотруднику зоопарка. Мы свяжемся с вами в ближайшее время."
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "no_contact", ContactState.waiting_confirm)
async def no_contact(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Ок, возвращайтесь, если понадобится помощь!")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "restart")
async def restart_quiz(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Новая попытка!", reply_markup=get_start_keyboard())
    await callback.answer()

@router.callback_query(F.data == "feedback")
async def leave_feedback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишите ваш отзыв о викторине. Мы обязательно его прочитаем!")
    await state.set_state(FeedbackState.waiting_message)
    await callback.answer()