from aiogram import Bot, Dispatcher
from app.bot.handlers import main as main_router
from app.bot.handlers import nutritions as nutritions_router
from app.bot.handlers import monitoring as monitoring_router

async def main():
    bot = Bot(token='7358236100:AAElSOcjgvMz1cvKzY-nlYQ3-QS4Z_i5hJo')
    dp = Dispatcher()

    dp.include_routers(main_router.router, monitoring_router.router, nutritions_router.router)

    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)