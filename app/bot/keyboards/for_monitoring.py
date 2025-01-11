from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_kb_for_send_data_class(_class: str):
    kb = ReplyKeyboardBuilder()
    for count in [str(i) for i in range(0, 11)]:
        kb.add()
        kb.button(text=f'{_class}-{count}')
    kb.button(text='Назад')
    kb.adjust(4, 4, 4)
    return kb.as_markup(resize_keyboard=True)