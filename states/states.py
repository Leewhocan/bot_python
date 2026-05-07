from aiogram.fsm.state import State, StatesGroup

class QuizState(StatesGroup):
    in_progress = State()
    current_question = State()

class FeedbackState(StatesGroup):
    waiting_message = State()

class ContactState(StatesGroup):
    waiting_confirm = State()