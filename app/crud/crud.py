from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import BaseCRUD
from models.db import connection
from models.models import User, Dish, Menu


class UserCRUD(BaseCRUD):
    model = User

class DishCRUD(BaseCRUD):
    model = Dish

class MenuCRUD(BaseCRUD):
    model = Menu

@connection
async def create_user(login: str, password: str, session: AsyncSession) -> int:
    user = User(login=login, password=password)
    session.add(user)
    await session.commit()
    return user.id
