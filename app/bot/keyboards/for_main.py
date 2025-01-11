from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Питание")
    kb.button(text="Мониторинг заболеваемости")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)