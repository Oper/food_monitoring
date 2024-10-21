import datetime
from datetime import date, timedelta

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name='main.html')


@app.get('/nutritions/', response_class=HTMLResponse)
async def nutritions(request: Request):
    title = 'Питание МБОУ "СОШ№1" г.Емвы'

    date_todey = date.today()
    date_left = date_todey - timedelta(days=2)
    date_right = date_todey + timedelta(days=3)
    #TODO
    # тестовый список меню
    menu_list = [date_todey, date_todey + timedelta(days=1), date_todey + timedelta(days=2), date_todey - timedelta(days=1), date_todey - timedelta(days=2)]

    return templates.TemplateResponse(request=request, name='nutritions.html', context={'title': title, 'date_todey': date_todey, 'menu_list': menu_list, 'date_left': date_left, 'date_right': date_right})


@app.get('/nutritions/{menu}', response_class=HTMLResponse)
async def date_menu(menu: str, request: Request):
    title = 'Меню на ' + str(menu)
    menu_today = {}

    return templates.TemplateResponse(request=request, name='menu_today.html', context={'title': title, 'menu': menu_today})
