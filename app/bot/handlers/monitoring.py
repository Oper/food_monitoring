from datetime import date, timedelta

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.bot.utils import get_class_all
from app.bot.keyboards.for_monitoring import get_kb_for_send_data_class
from app.db import session_manager
from crud.crud import ClassCRUD
from schemas.classes import ClassPydanticOne, ClassDataPydantic

router = Router()


@router.message(F.text.lower() == "мониторинг заболеваемости")
async def with_monitoring(message: Message):
    menu_list = await get_class_all()
    kb = ReplyKeyboardBuilder()
    for item_menu in menu_list:
        kb.add(KeyboardButton(text=item_menu))
    kb.add(KeyboardButton(text='Назад'))
    kb.adjust(4)
    await message.answer(
        'Выбрать класс:',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(F.text.regexp(r"\d{1,2}\D{1}-\d"))
@session_manager.connection()
async def send_data_class(message: Message, session, **kwargs):
    list_data = message.text.split('-')
    name_class = list_data[0]
    count_ill = int(list_data[1])
    date_send = date.today()
    try:
        current_class = await ClassCRUD.get_class_by_one(session=session, name_class=name_class)

        proc_ill = 0 if count_ill == 0 else round(count_ill * 100 / current_class.count_class)
        if current_class:
            if current_class.closed:
                await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                       values=ClassDataPydantic(
                                           count_ill=count_ill,
                                           proc_ill=proc_ill,
                                           closed=current_class.closed,
                                           date=date_send,
                                           date_open=current_class.date_open,
                                           date_closed=current_class.date_closed
                                       ))
            elif proc_ill > 20:
                await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                       values=ClassDataPydantic(
                                           count_ill=count_ill,
                                           proc_ill=proc_ill,
                                           closed=True,
                                           date=date_send,
                                           date_open=date_send + timedelta(days=7),
                                           date_closed=date_send + timedelta(days=1)
                                       ))
            else:
                await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                       values=ClassDataPydantic(
                                           count_ill=count_ill,
                                           proc_ill=proc_ill,
                                           closed=False,
                                           date=date_send,
                                           date_open=None,
                                           date_closed=None
                                       ))
        await message.answer(f'Данные по классу {list_data[0]} отправлены', reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f'Данные по классу {list_data[0]} НЕ ОТПРАВЛЕНЫ! Ошибка: {e}', reply_markup=ReplyKeyboardRemove())




@router.message(F.text.regexp(r"\d{1,2}\D{1}"))
async def set_class_for_send(message: Message):
    _class = message.text
    msg = f'Вы выбрали класс: {_class}\n' \
          f'Укажите количество болеющих:'
    await message.answer(msg, reply_markup=get_kb_for_send_data_class(_class))
