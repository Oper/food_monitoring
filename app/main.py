from datetime import date, datetime
from typing import Annotated
from venv import logger

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse


from auth.dependencies import get_current_user
from auth.models import User
from crud.crud import MenuCRUD, DishCRUD
from auth.router import router as router_auth
from db import SessionDep

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class DishPydanticIn(BaseModel):
    title: str
    recipe: int
    out_gramm: int
    price: float
    calories: float
    protein: float
    fats: float
    carb: float
    section: str

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class DishPydantic(DishPydanticIn):
    id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class DishPydanticEdit(BaseModel):
    id: int

class MenuPydantic(BaseModel):
    date_menu: date
    type_menu: str
    category_menu: str
    dish_id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class MenuPydanticEdit(BaseModel):
    id: int


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name='main.html')


@app.get('/nutritions/', response_class=HTMLResponse)
async def nutritions(request: Request, session: AsyncSession = SessionDep):
    title = 'Питание МБОУ "СОШ№1" г.Емвы'
    menu_list = []
    current_date = date.today().isoformat()
    row = await MenuCRUD.get_all(session=session)
    if row:
        for _ in row:
            cur_menu = str(_.date_menu)
            if cur_menu not in menu_list:
                menu_list.append(cur_menu)
    menu_list.sort()

    return templates.TemplateResponse(request=request, name='nutritions.html',
                                      context={'title': title, 'date_todey': current_date, 'menu_list': menu_list})


@app.get('/nutritions/{menu}', response_class=HTMLResponse)
async def menu_in_date(menu: str, request: Request, session: AsyncSession = SessionDep):
    title = 'Меню на ' + str(menu)
    current_menu = datetime.strptime(menu, "%Y-%m-%d").date()
    menus_db_by_day = await MenuCRUD.get_all_menus_by_one_day(session=session, day=current_menu)
    menu_today = {}
    if menus_db_by_day:
        for _ in menus_db_by_day:
            if _.category_menu not in menu_today:
                menu_today[_.category_menu] = {}
            if _.type_menu not in menu_today[_.category_menu]:
                menu_today[_.category_menu][_.type_menu] = []
            dish = await DishCRUD.get_dish_by_id(session=session, dish_id=_.dish_id)
            if dish:
                menu_today[_.category_menu][_.type_menu].append({
                    'dish_name': dish.title,
                    'out_gramm': dish.out_gramm,
                    'calories': dish.calories,
                    'price': dish.price,
                })

    return templates.TemplateResponse(request=request, name='menu_today.html',
                                      context={'title': title, 'menu': menu_today})


@app.post('/send_dish/')
async def create_dish(request: Request, data: Annotated[DishPydanticIn, Form()], session: AsyncSession = SessionDep):
    try:
        new_dish = await DishCRUD.add(session=session, title=data.title, recipe=data.recipe, out_gramm=data.out_gramm, price=data.price, calories=data.calories, protein=data.protein, fats=data.fats, carb=data.carb, section=data.section)
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin:tehnolog').include_query_params(msg="Succesfully created!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post('/send_menu/')
async def create_menu(request: Request, data: Annotated[MenuPydantic, Form()], session: AsyncSession = SessionDep):
    try:
        new_menu = await MenuCRUD.add(session=session, date_menu=data.date_menu, type_menu=data.type_menu, category_menu=data.category_menu, dish_id=data.dish_id)
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin:tehnolog').include_query_params(msg="Succesfully created!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post('/del_dish/')
async def delete_dish(request: Request, data: Annotated[DishPydanticEdit, Form()], session: AsyncSession = SessionDep):
    try:
        await DishCRUD.delete(session=session, id=data.id)
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin:tehnolog').include_query_params(msg="Succesfully deleted!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post('/del_menu/')
async def delete_menu(request: Request, data: Annotated[MenuPydanticEdit, Form()], session: AsyncSession = SessionDep):
    try:
        await MenuCRUD.delete(session=session, id=data.id)
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin:tehnolog').include_query_params(msg="Succesfully deleted!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post('/edit_dish/')
async def edit_dish(request: Request, data: Annotated[DishPydanticEdit, Form()], session: AsyncSession = SessionDep):
    dish = await DishCRUD.get_dish_by_id(session=session, dish_id=data.id)
    try: #TODO
        pass
    except Exception as e:
        logger.error(e)
    # redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully edit!")
    # return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    return app.url_path_for('admin:tehnolog')

@app.get('/admin-tehnolog/', name='admin:tehnolog', response_class=HTMLResponse)
async def admin_nutritions(request: Request, user_data: User = Depends(get_current_user), session: AsyncSession = SessionDep):
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
    menus_db = await MenuCRUD.get_all(session=session)
    if menus_db:
        for _ in menus_db:
            date = _.date_menu.isoformat()
            if date not in menus:
                menus[date] = {}
            if _.category_menu not in menus[date]:
                menus[date][_.category_menu] = {}
            if _.type_menu not in menus[date][_.category_menu]:
                menus[date][_.category_menu][_.type_menu] = []
            dish = await DishCRUD.get_dish_by_id(session=session, dish_id=_.dish_id)

            menus[date][_.category_menu][_.type_menu].append({
                'menu_id': _.id,
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


    return templates.TemplateResponse(request=request, name='admin_nutritions.html',
                                      context={'title': title, 'dishes': dishes, 'menus': menus})


@app.get('/login')
async def login(request: Request):
    title = 'Авторизация'
    return templates.TemplateResponse(request=request, name='login.html', context={'title': title})

@app.get('/register')
async def register(request: Request):
    title = 'Регистрация'
    return templates.TemplateResponse(request=request, name='register.html', context={'title': title})

app.include_router(router_auth)

@app.get('/404')
async def not_found(request: Request):
    title = 'Страница не найдена'
    return templates.TemplateResponse(request=request, name='404.html', context={'title': title})