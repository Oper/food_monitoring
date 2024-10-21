from datetime import datetime

from sqlalchemy import JSON, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.db import Base


class User(Base):
    __tablename__ = 'users'

    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(unique=True)

class Dish(Base):
    __tablename__ = 'dishes'

    title: Mapped[str]
    recipe: Mapped[int]
    out_gramm: Mapped[int]
    price: Mapped[float]
    prop_dish: Mapped[dict] = mapped_column(JSON)
    menus: Mapped[list['Menu']] = relationship(
        'Menu',
        back_populates='dish',
        cascade='all, delete-orphan'
    )


class Menu(Base):
    __tablename__ = 'menus'

    date_menu: Mapped[datetime] = mapped_column(server_default=func.now())
    type_menu: Mapped[str]
    category_menu: Mapped[str]
    dish_id: Mapped[int] = mapped_column(ForeignKey('dishes.id'))
    dish: Mapped['Dish'] = relationship(
        'Dish',
        back_populates='menus'
    )