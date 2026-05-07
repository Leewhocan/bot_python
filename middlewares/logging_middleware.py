import logging
from aiogram.types import Update
from aiogram import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Безопасное логирование обновления: используем repr() вместо model_dump_json()
        logging.info(f"Update: {repr(event)}")
        return await handler(event, data)