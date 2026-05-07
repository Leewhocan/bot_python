import aiosqlite
import logging

DB_PATH = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                animal TEXT NOT NULL,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    logging.info("Database initialized")

async def save_quiz_result(user_id: int, username: str, animal: str, score: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO quiz_results (user_id, username, animal, score) VALUES (?, ?, ?, ?)",
            (user_id, username, animal, score)
        )
        await db.commit()

async def save_feedback(user_id: int, username: str, message: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO feedback (user_id, username, message) VALUES (?, ?, ?)",
            (user_id, username, message)
        )
        await db.commit()

async def get_recent_feedbacks(limit: int = 10) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, username, message, timestamp FROM feedback ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return await cursor.fetchall()

async def get_stats() -> dict:
    """Возвращает статистику по викторинам."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Общее количество прохождений
        total_cursor = await db.execute("SELECT COUNT(*) FROM quiz_results")
        total = (await total_cursor.fetchone())[0]

        # Топ животных
        top_cursor = await db.execute(
            "SELECT animal, COUNT(*) as cnt FROM quiz_results GROUP BY animal ORDER BY cnt DESC"
        )
        top_animals = await top_cursor.fetchall()

        # Последние 5 прохождений
        recent_cursor = await db.execute(
            "SELECT user_id, username, animal, timestamp FROM quiz_results ORDER BY id DESC LIMIT 5"
        )
        recent = await recent_cursor.fetchall()

        return {
            "total": total,
            "top_animals": top_animals,
            "recent": recent
        }