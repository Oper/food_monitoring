import os
from datetime import date, datetime
from typing import Annotated
from venv import logger

from fastapi import APIRouter, Request, Form, Depends
from openpyxl.reader.excel import load_workbook
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.db import SessionDep
from app.crud.crud import MenuCRUD, DishCRUD
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.schemas.dishes import DishPydanticIn, DishPydanticTitle, DishPydanticEdit
from app.schemas.menus import MenuPydanticListIn, MenuPydantic, MenuPydanticEdit

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix='/nutritions', tags=['food'])


@router.get('/', response_class=HTMLResponse)
async def nutritions(request: Request, session: AsyncSession = SessionDep):
    title = 'Питание МБОУ "СОШ№1" г.Емвы'
    menu_list = []
    current_date = date.today().isoformat()
    try:
        all_menus = await MenuCRUD.get_all(session=session)
        if all_menus:
            for menu in all_menus:
                cur_menu = str(menu.date_menu)
                if cur_menu not in menu_list:
                    menu_list.append(cur_menu)
        menu_list.sort()
    except Exception as e:
        logger.error(e)

    return templates.TemplateResponse(request=request, name='nutritions.html',
                                      context={'title': title, 'date_todey': current_date, 'menu_list': menu_list})


@router.get('/admin', response_class=HTMLResponse)
async def admin_nutritions(request: Request, user_data: User = Depends(get_current_user),
                           session: AsyncSession = SessionDep):
    title = 'Панель управления технолога'
    dishes = {}
    dishes_db = await DishCRUD.get_all(session=session)
    for row in dishes_db:
        dish = row.to_dict()
        if dish['title'] not in dishes:
            dishes[dish['title']] = []
        dishes[dish['title']].append({
            'id': dish['id'],
            'recipe': dish['recipe'],
            'out_gramm': dish['out_gramm'],
            'calories': dish['calories'],
            'protein': dish['protein'],
            'fats': dish['fats'],
            'carb': dish['carb'],
            'price': dish['price'],
        })

    menus = {}
    menus_db = await MenuCRUD.get_all_menus_by_five_day(session=session)
    result_menus = {}

    if menus_db:
        for menu in menus_db:
            date = menu.date_menu.isoformat()
            if date not in result_menus:
                result_menus[date] = {}
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
            if menu.category_menu == '1-4 классы' and menu.type_menu == 'Завтрак':
                result_menus[date]['cal_breakfast'] = result_menus[date].get('cal_breakfast', 0) + dish.calories
                result_menus[date]['out_breakfast'] = result_menus[date].get('out_breakfast', 0) + dish.out_gramm

            if menu.category_menu == '1-4 классы' and menu.type_menu == 'Обед':
                result_menus[date]['cal_lunch'] = result_menus[date].get('cal_lunch', 0) + dish.calories
                result_menus[date]['out_lunch'] = result_menus[date].get('out_lunch', 0) + dish.out_gramm

    return templates.TemplateResponse(request=request, name='admin_nutritions.html',
                                      context={'title': title, 'dishes': dishes, 'menus': menus,
                                               'result': result_menus})


@router.get('/{menu}', response_class=HTMLResponse)
async def menu_in_date(date_menu: str, request: Request, session: AsyncSession = SessionDep):
    title = 'Меню на ' + str(date_menu)
    current_menu = datetime.strptime(date_menu, "%Y-%m-%d").date()
    menus_db_by_day = await MenuCRUD.get_all_menus_by_one_day(session=session, day=current_menu)
    menu_today = {}
    if menus_db_by_day:
        for menu in menus_db_by_day:
            if menu.category_menu not in menu_today:
                menu_today[menu.category_menu] = {}
            if menu.type_menu not in menu_today[menu.category_menu]:
                menu_today[menu.category_menu][menu.type_menu] = []
            dish = await DishCRUD.get_dish_by_id(session=session, dish_id=menu.dish_id)
            if dish:
                menu_today[menu.category_menu][menu.type_menu].append({
                    'dish_name': dish.title,
                    'out_gramm': dish.out_gramm,
                    'calories': dish.calories,
                    'price': dish.price,
                })

    return templates.TemplateResponse(request=request, name='menu_today.html',
                                      context={'title': title, 'menu': menu_today})


@router.post('/send_dish/')
async def create_dish(request: Request, data: Annotated[DishPydanticIn, Form()], session: AsyncSession = SessionDep):
    try:
        dish = await DishCRUD.get_dish_by_name(session=session, dish_name=data.title)
        if dish:
            await DishCRUD.update(session=session, filters=DishPydanticTitle(title=data.title), values=data)
            redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully update!")
            return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

        else:
            await DishCRUD.add(session=session, values=data)
            redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully created!")
            return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(e)
    return templates.TemplateResponse(request=request, name='404.html')


@router.post('/send_menu/')
async def create_menu(request: Request, data: Annotated[MenuPydanticListIn, Form()],
                      session: AsyncSession = SessionDep):
    menu_dict = data.model_dump()
    try:
        for id in menu_dict['dishs_ids']:
            await MenuCRUD.add(session=session, values=MenuPydantic(
                date_menu=menu_dict['date_menu'],
                type_menu=menu_dict['type_menu'],
                category_menu=menu_dict['category_menu'],
                dish_id=id))
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully created!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/del_dish/')
async def delete_dish(request: Request, data: Annotated[DishPydanticEdit, Form()], session: AsyncSession = SessionDep):
    id_dish = data.id
    try:
        await DishCRUD.delete(session=session, filters=DishPydanticEdit(id=id_dish))
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully deleted!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/del_menu/')
async def delete_menu(request: Request, data: Annotated[MenuPydanticEdit, Form()], session: AsyncSession = SessionDep):
    id_menu = data.id
    try:
        await MenuCRUD.delete(session=session, filters=MenuPydanticEdit(id=id_menu))
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully deleted!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get('/download/{menu}')
async def get_file_menu_for_monitoring(date_menu: str, session: AsyncSession = SessionDep):
    wb = load_workbook(filename='templates/GGGG-MM-DD-sm.xlsx')
    sheet = wb['1']
    current_date_menu = datetime.strptime(date_menu, "%Y-%m-%d").date()
    sheet['J1'] = current_date_menu
    result_filename = date_menu + '-sm.xlsx'
    menus_db_by_day = await MenuCRUD.get_category_menus_one_day(session=session, day=current_date_menu)
    if menus_db_by_day:
        for menu in menus_db_by_day:
            dish = await DishCRUD.get_dish_by_id(session=session, dish_id=menu.dish_id)
            if menu.type_menu == 'Завтрак':
                if dish.section == 'гор.блюдо':
                    if dish.recipe != 0:
                        sheet['C4'] = dish.recipe
                    sheet['D4'] = dish.title
                    sheet['E4'] = dish.out_gramm
                    sheet['F4'] = dish.price
                    sheet['G4'] = dish.calories
                    sheet['H4'] = dish.protein
                    sheet['I4'] = dish.fats
                    sheet['J4'] = dish.carb
                elif dish.section == 'гор.напиток':
                    if dish.recipe != 0:
                        sheet['C5'] = dish.recipe
                    sheet['D5'] = dish.title
                    sheet['E5'] = dish.out_gramm
                    sheet['F5'] = dish.price
                    sheet['G5'] = dish.calories
                    sheet['H5'] = dish.protein
                    sheet['I5'] = dish.fats
                    sheet['J5'] = dish.carb
                elif dish.section == 'Хлеб':
                    sheet['D6'] = dish.title
                    sheet['E6'] = dish.out_gramm
                    sheet['F6'] = dish.price
                    sheet['G6'] = dish.calories
                    sheet['H6'] = dish.protein
                    sheet['I6'] = dish.fats
                    sheet['J6'] = dish.carb
                elif dish.section == 'Нет' and not sheet['D7'].value:
                    if dish.recipe != 0:
                        sheet['C7'] = dish.recipe
                    sheet['D7'] = dish.title
                    sheet['E7'] = dish.out_gramm
                    sheet['F7'] = dish.price
                    sheet['G7'] = dish.calories
                    sheet['H7'] = dish.protein
                    sheet['I7'] = dish.fats
                    sheet['J7'] = dish.carb
                else:
                    if dish.recipe != 0:
                        sheet['C8'] = dish.recipe
                    sheet['D8'] = dish.title
                    sheet['E8'] = dish.out_gramm
                    sheet['F8'] = dish.price
                    sheet['G8'] = dish.calories
                    sheet['H8'] = dish.protein
                    sheet['I8'] = dish.fats
                    sheet['J8'] = dish.carb
            elif menu.type_menu == 'Обед':
                if dish.section == 'фрукты':
                    if dish.recipe != 0:
                        sheet['C9'] = dish.recipe
                    sheet['D9'] = dish.title
                    sheet['E9'] = dish.out_gramm
                    sheet['G9'] = dish.calories
                    sheet['H9'] = dish.protein
                    sheet['I9'] = dish.fats
                    sheet['J9'] = dish.carb
                elif dish.section == 'закуска':
                    if dish.recipe != 0:
                        sheet['C12'] = dish.recipe
                    sheet['D12'] = dish.title
                    sheet['E12'] = dish.out_gramm
                    sheet['G12'] = dish.calories
                    sheet['H12'] = dish.protein
                    sheet['I12'] = dish.fats
                    sheet['J12'] = dish.carb
                elif dish.section == '1 блюдо':
                    if dish.recipe != 0:
                        sheet['C13'] = dish.recipe
                    sheet['D13'] = dish.title
                    sheet['E13'] = dish.out_gramm
                    sheet['G13'] = dish.calories
                    sheet['H13'] = dish.protein
                    sheet['I13'] = dish.fats
                    sheet['J13'] = dish.carb
                elif dish.section == '2 блюдо':
                    if dish.recipe != 0:
                        sheet['C14'] = dish.recipe
                    sheet['D14'] = dish.title
                    sheet['E14'] = dish.out_gramm
                    sheet['G14'] = dish.calories
                    sheet['H14'] = dish.protein
                    sheet['I14'] = dish.fats
                    sheet['J14'] = dish.carb
                elif dish.section == 'гарнир':
                    if dish.recipe != 0:
                        sheet['C15'] = dish.recipe
                    sheet['D15'] = dish.title
                    sheet['E15'] = dish.out_gramm
                    sheet['G15'] = dish.calories
                    sheet['H15'] = dish.protein
                    sheet['I15'] = dish.fats
                    sheet['J15'] = dish.carb
                elif dish.section == 'сладкое':
                    if dish.recipe != 0:
                        sheet['C16'] = dish.recipe
                    sheet['D16'] = dish.title
                    sheet['E16'] = dish.out_gramm
                    sheet['G16'] = dish.calories
                    sheet['H16'] = dish.protein
                    sheet['I16'] = dish.fats
                    sheet['J16'] = dish.carb
                elif dish.section == 'хлеб бел.':
                    sheet['D17'] = dish.title
                    sheet['E17'] = dish.out_gramm
                    sheet['G17'] = dish.calories
                    sheet['H17'] = dish.protein
                    sheet['I17'] = dish.fats
                    sheet['J17'] = dish.carb
                elif dish.section == 'хлеб черн.':
                    sheet['D18'] = dish.title
                    sheet['E18'] = dish.out_gramm
                    sheet['G18'] = dish.calories
                    sheet['H18'] = dish.protein
                    sheet['I18'] = dish.fats
                    sheet['J18'] = dish.carb
                elif dish.section == 'Нет' and not sheet['D19'].value:
                    if dish.recipe != 0:
                        sheet['C19'] = dish.recipe
                    sheet['D19'] = dish.title
                    sheet['E19'] = dish.out_gramm
                    sheet['G19'] = dish.calories
                    sheet['H19'] = dish.protein
                    sheet['I19'] = dish.fats
                    sheet['J19'] = dish.carb
                else:
                    if dish.recipe != 0:
                        sheet['C20'] = dish.recipe
                    sheet['D20'] = dish.title
                    sheet['E20'] = dish.out_gramm
                    sheet['G20'] = dish.calories
                    sheet['H20'] = dish.protein
                    sheet['I20'] = dish.fats
                    sheet['J20'] = dish.carb

    patch_file = os.path.join('tmp', result_filename)
    try:

        if os.path.exists('tmp'):
            wb.save(patch_file)
            logger.info('Создаем файл в папке - tmp')
        else:
            os.mkdir('tmp')
            logger.info('Создали папку, т.к. ее нет')
            wb.save(patch_file)
            logger.info('Создаем файл в папке - tmp')
    except Exception as e:
        logger.error(e)
    return FileResponse(path=patch_file, filename=result_filename, media_type='multipart/form-data')
