from aiogram import Router, types
from aiogram.filters import Command
from config import ADMIN_ID
from database.db import get_recent_feedbacks, get_stats

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(Command("feedbacks"))
async def cmd_feedbacks(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав.")
        return

    feedbacks = await get_recent_feedbacks(limit=10)
    if not feedbacks:
        await message.answer("Пока ещё нет отзывов.")
        return

    text = "📝 <b>Последние отзывы:</b>\n\n"
    for idx, (user_id, username, msg, timestamp) in enumerate(feedbacks, 1):
        user_str = f"@{username}" if username.strip() else f"ID{user_id}"
        text += f"{idx}. {user_str} ({timestamp}):\n{msg}\n\n"
    await message.answer(text[:4000])

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав.")
        return

    stats = await get_stats()
    total = stats["total"]
    top = stats["top_animals"]
    recent = stats["recent"]

    text = f"📊 <b>Статистика викторины</b>\n\n"
    text += f"Всего прохождений: <b>{total}</b>\n\n"
    if top:
        text += "<b>Популярные животные:</b>\n"
        for animal, cnt in top[:5]:
            text += f"• {animal}: {cnt} раз(а)\n"
    if recent:
        text += "\n<b>Последние результаты:</b>\n"
        for user_id, username, animal, timestamp in recent:
            user_str = f"@{username}" if username.strip() else f"ID{user_id}"
            text += f"• {user_str} → {animal} ({timestamp})\n"
    await message.answer(text)