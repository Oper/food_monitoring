from datetime import date, timedelta, datetime

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict
from starlette import status
from starlette.responses import RedirectResponse

from crud.crud import MenuCRUD, DishCRUD
from models.db import connection

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class DishPydantic(BaseModel):
    id: int
    title: str
    recipe: int
    out_gramm: int
    price: float
    calories: float
    protein: float
    fats: float
    carb: float

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class MenuPydantic(BaseModel):
    date_menu: datetime
    type_menu: str
    category_menu: str
    dish_id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

@connection
async def get_menus(session):
    row = await MenuCRUD.get_all(session)
    if row:
        return row
    return {'message': 'Меню не найдено!'}

@connection
async def get_menus_by_day(session, date_menu: date):
    row = await MenuCRUD.get_all_menus_by_one_day(session, date_menu)
    if row:
        return row
    return {'message': 'Меню не найдено!'}

@connection
async def get_dishes(session):
    dishes = await DishCRUD.get_all(session)
    return dishes

@connection
async def add_dish(session, **kwargs):
    return await DishCRUD.add(session, **kwargs)

@connection
async def add_menu(session, **kwargs):
    return await MenuCRUD.add(session, **kwargs)

@connection
async def get_dish_by_id(session, dish_id: int):
    row = await DishCRUD.get_dish_by_id(session, dish_id)
    if row:
        return DishPydantic.from_orm(row).dict()
    return {'message': f'Блюдо с ID {dish_id} не найдено!'}


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name='main.html')


@app.get('/nutritions/', response_class=HTMLResponse)
async def nutritions(request: Request):
    title = 'Питание МБОУ "СОШ№1" г.Емвы'
    menu_list = []
    current_date = date.today()
    row = await get_menus()
    if row:
        for _ in row:
            if _.date_menu.isoformat() not in menu_list:
                menu_list.append(_.date_menu.isoformat())
    menu_list.sort()
    print(current_date)
    return templates.TemplateResponse(request=request, name='nutritions.html',
                                      context={'title': title, 'date_todey': current_date, 'menu_list': menu_list})


@app.get('/nutritions/{menu}', response_class=HTMLResponse)
async def menu_in_date(menu: str, request: Request):
    title = 'Меню на ' + str(menu)
    current_menu = datetime.strptime(menu, "%Y-%m-%d").date()
    menus_db_by_day = await get_menus_by_day(date_menu=current_menu)
    menu_today = {}
    if menus_db_by_day:
        for _ in menus_db_by_day:
            print(_.category_menu)
            if _.category_menu not in menu_today:
                menu_today[_.category_menu] = {}
            if _.type_menu not in menu_today[_.category_menu]:
                menu_today[_.category_menu][_.type_menu] = []
            dish = await get_dish_by_id(dish_id=_.dish_id)
            if dish:
                menu_today[_.category_menu][_.type_menu].append({
                    'dish_name': dish['title'],
                    'out_gramm': dish['out_gramm'],
                    'calories': dish['calories'],
                    'price': dish['price'],
                })



    return templates.TemplateResponse(request=request, name='menu_today.html',
                                      context={'title': title, 'menu': menu_today})


@app.post('/send_dish/')
async def create_dish(request: Request, title = Form(), recipe = Form(), out_gramm = Form(), price = Form(), calories = Form(), protein = Form(), fats = Form(), carb = Form()):
    new_dish = await add_dish(title=title, recipe=int(recipe), out_gramm=int(out_gramm),
                              price=float(price), calories=float(calories), protein=float(protein), fats=float(fats), carb=float(carb))
    redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully created!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post('/send_menu/')
async def create_menu(request: Request, date = Form(), type = Form(), category = Form(), dish = Form()):
    date_menu = date.strptime(date, '%Y-%m-%d')
    new_menu = await add_menu(date_menu=date_menu, type_menu=type, category_menu=category, dish_id=int(dish))
    redirect_url = request.url_for('admin_nutritions').include_query_params(msg="Succesfully created!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.get('/admin-tehnolog/', response_class=HTMLResponse)
async def admin_nutritions(request: Request):
    title = 'Панель управления технолога'
    dishes = {}
    dishes_db = await get_dishes()
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
    menus_db = await get_menus()
    for _ in menus_db:
        date = _.date_menu.isoformat()
        if date not in menus:
            menus[date] = {}
        if _.category_menu not in menus[date]:
            menus[date][_.category_menu] = {}
        if _.type_menu not in menus[date][_.category_menu]:
            menus[date][_.category_menu][_.type_menu] = []
        dish = await get_dish_by_id(dish_id=_.dish_id)
        print(menus)
        menus[date][_.category_menu][_.type_menu].append({
            'dish_id': dish['id'],
            'dish_title': dish['title'],
            'dish_out': dish['out_gramm'],
            'dish_recipe': dish['recipe'],
            'dish_calories': dish['calories'],
            'dish_protein': dish['protein'],
            'dish_fats': dish['fats'],
            'dish_carb': dish['carb'],
            'dish_price': dish['price']
        })
    print(menus_db)
    print(*menus)
    return templates.TemplateResponse(request=request, name='admin_nutritions.html',
                                      context={'title': title, 'dishes': dishes, 'menus': menus})