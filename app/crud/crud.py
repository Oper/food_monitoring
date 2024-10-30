from datetime import timedelta, date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import BaseCRUD
from models.models import User, Dish, Menu


class UserCRUD(BaseCRUD):
    model = User



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