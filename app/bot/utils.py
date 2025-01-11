import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import session_manager
from app.crud.crud import MenuCRUD, DishCRUD, ClassCRUD
from app.schemas.classes import ClassPydanticOne, ClassDataPydantic


@session_manager.connection()
async def get_five_menus(session: AsyncSession) -> list[str]:
    menus = await MenuCRUD.get_all_menus_by_five_day(session=session)
    list_menus = []
    for menu in menus:
        cur_menu = str(menu.date_menu)
        if cur_menu not in list_menus:
            list_menus.append(cur_menu)
    list_menus.sort()
    return list_menus


@session_manager.connection()
async def get_menus_by_day(session: AsyncSession) -> dict:
    menus_db = await MenuCRUD.get_all_menus_by_five_day(session=session)
    menus = {}
    if menus_db:
        for menu in menus_db:
            date = menu.date_menu.isoformat()
            if date not in menus:
                menus[date] = {}
            if menu.category_menu not in menus[date]:
                menus[date][menu.category_menu] = {}
            if menu.type_menu not in menus[date][menu.category_menu]:
                menus[date][menu.category_menu][menu.type_menu] = []
            dish = await DishCRUD.get_dish_by_id(session=session, dish_id=menu.dish_id)

            menus[date][menu.category_menu][menu.type_menu].append({
                'menu_id': menu.id,
                'dish_id': dish.id,
                'dish_title': dish.title,
                'dish_out': dish.out_gramm,
                'dish_recipe': dish.recipe,
                'dish_calories': dish.calories,
                'dish_protein': dish.protein,
                'dish_fats': dish.fats,
                'dish_carb': dish.carb,
                'dish_price': dish.price,
            })
    return menus


@session_manager.connection()
async def get_class_all(session: AsyncSession) -> list:
    all_classes = []
    _classes = await ClassCRUD.get_all(session=session)
    if _classes:
        for _class in _classes:
            all_classes.append(_class.name_class)
    return all_classes


@session_manager.connection()
async def update_class(name_class: str, count_ill: int, session: AsyncSession):
    date_send = datetime.datetime.today()
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
                                           date_open=date_send + datetime.timedelta(days=7),
                                           date_closed=date_send + datetime.timedelta(days=1)
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

    except Exception as e:
        return f'Ошибка отправки данных'
