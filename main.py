import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import init_db
from handlers import start, quiz, result, feedback, admin
from middlewares.logging_middleware import LoggingMiddleware

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(LoggingMiddleware())

    dp.include_router(start.router)
    dp.include_router(quiz.router)
    dp.include_router(result.router)
    dp.include_router(feedback.router)
    dp.include_router(admin.router)   

    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())