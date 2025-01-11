from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.for_main import get_main_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Выберите раздел",
        reply_markup=get_main_kb()
    )


@router.message(F.text.lower() == "назад")
async def call_back(message: Message):
    await message.answer(
        "Выберите раздел",
        reply_markup=get_main_kb()
    )
