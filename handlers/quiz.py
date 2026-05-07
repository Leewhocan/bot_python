import logging
import asyncio
import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from keyboards.keyboards import get_answer_keyboard, get_result_keyboard
from states.states import QuizState
from data.quiz_data import QUESTIONS
from utils.scoring import calculate_animal
from database.db import save_quiz_result
from config import ADMIN_ID

router = Router()

MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 МБ

def _user_display(user) -> str:
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    else:
        return f"ID{user.id}"

@router.callback_query(F.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(QuizState.in_progress)
    await state.update_data(current_question=0, answers_weights=[])
    await ask_question(callback.message, state, 0)
    await callback.answer()

async def ask_question(message: types.Message, state: FSMContext, q_idx: int):
    question = QUESTIONS[q_idx]
    options = [opt["text"] for opt in question["options"]]
    await message.answer(
        f"Вопрос {q_idx + 1}/{len(QUESTIONS)}:\n{question['text']}",
        reply_markup=get_answer_keyboard(options)
    )
    await state.update_data(current_question=q_idx)

@router.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    choice_idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    current_q = data["current_question"]
    question = QUESTIONS[current_q]

    selected_option = question["options"][choice_idx]
    answers_weights = data["answers_weights"] + [selected_option["weights"]]
    await state.update_data(answers_weights=answers_weights)

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    next_q = current_q + 1
    if next_q < len(QUESTIONS):
        await ask_question(callback.message, state, next_q)
    else:
        animal = calculate_animal(answers_weights)
        await state.update_data(animal=animal)

        # Сохраняем результат в БД
        user = callback.from_user
        await save_quiz_result(user.id, user.username or "", animal, 0)

        # Уведомление админу – асинхронно
        asyncio.create_task(_notify_admin(callback.bot, user, animal))

        await show_result(callback.message, animal)

    await callback.answer()

async def _notify_admin(bot, user, animal):
    display = _user_display(user)
    try:
        await bot.send_message(
            ADMIN_ID,
            f"✅ Пользователь {display} завершил викторину и получил животное: <b>{animal}</b>."
        )
    except Exception as e:
        logging.warning(f"Не удалось уведомить админа о результате: {e}")

async def show_result(message: types.Message, animal: str):
    from data.quiz_data import ANIMALS
    animal_data = ANIMALS[animal]
    image_path = animal_data["image"]

    try:
        file_size = os.path.getsize(image_path)
    except Exception:
        logging.exception("Не удалось получить размер файла")
        await message.answer(animal_data["description"])
        await message.answer("Что хотите сделать дальше?", reply_markup=get_result_keyboard())
        return

    if file_size > MAX_PHOTO_SIZE:
        logging.info(f"Файл {image_path} слишком большой ({file_size} байт), отправляю как документ")
        try:
            doc = FSInputFile(image_path)
            await message.answer_document(doc, caption=animal_data["description"])
        except Exception as e:
            logging.exception(f"Не удалось отправить документ: {e}")
            await message.answer(animal_data["description"])
    else:
        try:
            photo = FSInputFile(image_path)
            await message.answer_photo(photo, caption=animal_data["description"])
        except Exception as e:
            logging.warning(f"Не удалось отправить как фото ({e}). Пробую как документ.")
            try:
                doc = FSInputFile(image_path)
                await message.answer_document(doc, caption=animal_data["description"])
            except Exception as e2:
                logging.exception(f"Не удалось отправить файл: {e2}")
                await message.answer(animal_data["description"])

    await message.answer("Что хотите сделать дальше?", reply_markup=get_result_keyboard())