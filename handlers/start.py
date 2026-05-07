import random
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from keyboards.keyboards import get_start_keyboard, get_main_reply_keyboard

router = Router()

GREETINGS = [
    "Привет, {name}! Готов узнать своё тотемное животное? 🐾",
    "Здравствуй, {name}! Сегодня мы отправимся в увлекательное путешествие по миру Московского зоопарка! 🌍",
    "Добро пожаловать, {name}! Я помогу тебе подобрать животное, которое подходит тебе по духу. 😊",
    "Приветствую тебя, {name}! Давай узнаем, кто ты в мире животных? 🦒",
    "Привет, {name}! Пройди викторину – и получишь своего тотемного зверя и сюрприз! 🎁",
]

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Отправляем логотип, если файл существует
    try:
        logo = FSInputFile("assets/images/logo.png")
        await message.answer_photo(logo)
    except Exception:
        pass  # если логотипа нет, просто пропускаем
    
    greeting = random.choice(GREETINGS).format(name=message.from_user.first_name)
    await message.answer(
        greeting + "\n\nНажми кнопку ниже, чтобы начать викторину!",
        reply_markup=get_start_keyboard()
    )
    
    # Показываем кнопку перезапуска на постоянной клавиатуре
    await message.answer(
        "🔄 Для перезапуска викторины используйте кнопку на клавиатуре.",
        reply_markup=get_main_reply_keyboard()
    )

@router.message(F.text == "🔄 Попробовать ещё раз")
async def restart_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Давайте попробуем снова!", reply_markup=get_start_keyboard())