from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.bot.keyboards.for_main import get_main_kb
from app.bot.utils import get_five_menus, get_menus_by_day

router = Router()


@router.message(F.text.lower() == "питание")
async def with_nutritions(message: Message):
    menu_list = await get_five_menus()
    kb = ReplyKeyboardBuilder()
    for menu in menu_list:
        kb.button(text=menu)
    kb.button(text='Назад')
    kb.adjust(3)
    await message.answer(
        'Выбрать день:',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(F.text)
async def show_menu(message: Message):
    try:
        date_menu = message.text
        menu_list = await get_menus_by_day()
        current_menu = menu_list[date_menu]
        result = ''
        for c_key, t_value in current_menu.items():
            for t_key, dishes in t_value.items():
                result += f'<b>{c_key} - {t_key}:</b> \n'
                for dish in dishes:
                    if c_key == 'Продажа' or (c_key == '1-4 классы' and t_key == 'Завтрак'):
                        result += f'Блюдо: {dish.get('dish_title')}, Цена: {dish.get('dish_price')};\n'
                    else:
                        result += f'Блюдо: {dish.get('dish_title')};\n'

        await message.reply(result, parse_mode=ParseMode.HTML, reply_markup=get_main_kb())
    except Exception as e:
        await message.reply('Нет меню на этот день', reply_markup=get_main_kb())
