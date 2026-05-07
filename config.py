import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

staff_raw = os.getenv("STAFF_ID", "")
STAFF_IDS = [int(s.strip()) for s in staff_raw.split(",") if s.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не указан в .env")
if not STAFF_IDS:
    # если сотрудник не указан, заявки получает только админ
    STAFF_IDS = [ADMIN_ID]