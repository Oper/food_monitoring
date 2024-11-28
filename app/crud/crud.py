from datetime import timedelta, date

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.auth.models import User
from app.models.models import Dish, Menu


class UserCRUD(BaseCRUD):
    model = User

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int, session: AsyncSession):
        # Найти запись по ID
        logger.info(f"Поиск {cls.model.__name__} с ID: {data_id}")
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись с ID {data_id} найдена.")
            else:
                logger.info(f"Запись с ID {data_id} не найдена.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        # Найти одну запись по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись найдена по фильтрам: {filter_dict}")
            else:
                logger.info(f"Запись не найдена по фильтрам: {filter_dict}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Добавление записи {cls.model.__name__} с параметрами: {values_dict}")
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        try:
            await session.flush()
            logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise e
        return new_instance

class DishCRUD(BaseCRUD):
    model = Dish

    @classmethod
    async def get_dish_by_id(cls, session: AsyncSession, dish_id: int) -> Dish:
        query = select(cls.model).filter_by(id=dish_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

class MenuCRUD(BaseCRUD):
    model = Menu

    @classmethod
    async def get_all(cls, session: AsyncSession):
        current_date = date.today()
        left_date = current_date - timedelta(days=1)
        right_date = current_date + timedelta(days=1)
        query = select(cls.model).filter(and_(cls.model.date_menu >= left_date, cls.model.date_menu <= right_date))
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_all_menus_by_one_day(cls, session: AsyncSession, day: date):
        query = select(cls.model).filter(cls.model.date_menu == day)
        result = await session.execute(query)
        return result.scalars().all()