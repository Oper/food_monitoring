from contextlib import asynccontextmanager
from venv import logger

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.auth.router import router as router_auth
from app.routes.food_monitoring import router as router_food
from app.routes.san_monitoring import router as router_san
from app.scheduler.datasend import add_datasend, update_class
from app.scheduler.datasend import send_datasend


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом планировщика приложения

    Args:
        app (FastAPI): Экземпляр приложения FastAPI
    """
    try:
        # Настройка и запуск планировщика
        scheduler.add_job(
            add_datasend,
            'cron',
            day_of_week='mon-fri',
            hour='9-12',
            minute='*',
            id='add_datasend',
            replace_existing=True
        )
        scheduler.add_job(
            send_datasend,
            'cron',
            day_of_week='mon-fri',
            hour='9',
            minute='50-59/1',
            id='send_datasend',
            replace_existing=True
        )
        scheduler.add_job(
            update_class,
            'cron',
            hour='20',
            id='update_class',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Планировщик обновления и передачи данных запущен")
        yield
    except Exception as e:
        logger.error(f"Ошибка инициализации планировщика: {e}")
    finally:
        # Завершение работы планировщика
        scheduler.shutdown()
        logger.info("Планировщик остановлен")


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name='main.html')


@app.get('/login')
async def login(request: Request):
    title = 'Авторизация'
    return templates.TemplateResponse(request=request, name='login.html', context={'title': title})


@app.get('/register')
async def register(request: Request):
    title = 'Регистрация'
    return templates.TemplateResponse(request=request, name='register.html', context={'title': title})


app.include_router(router_auth)
app.include_router(router_food)
app.include_router(router_san)


@app.get('/404')
async def not_found(request: Request):
    title = 'Страница не найдена'
    return templates.TemplateResponse(request=request, name='404.html', context={'title': title})
