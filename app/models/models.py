import datetime
from datetime import date

from sqlalchemy import func, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Dish(Base):
    __tablename__ = 'dishes'

    title: Mapped[str]
    recipe: Mapped[int]
    out_gramm: Mapped[int]
    price: Mapped[float]
    calories: Mapped[float]
    protein: Mapped[float]
    fats: Mapped[float]
    carb: Mapped[float]
    menus: Mapped[list['Menu']] = relationship(
        'Menu',
        back_populates='dish',
        cascade='all, delete-orphan'
    )
    section: Mapped[str] = mapped_column(nullable=True)


class Menu(Base):
    __tablename__ = 'menus'

    date_menu: Mapped[date] = mapped_column(server_default=func.now())
    type_menu: Mapped[str]
    category_menu: Mapped[str]
    dish_id: Mapped[int] = mapped_column(ForeignKey('dishes.id'))
    dish: Mapped['Dish'] = relationship(
        'Dish',
        back_populates='menus'
    )


class Class(Base):
    __tablename__ = 'classes'

    name_class: Mapped[str] = mapped_column(unique=True)
    man_class: Mapped[str]
    count_ill: Mapped[int]
    count_class: Mapped[int]
    proc_ill: Mapped[int] = mapped_column(nullable=True)
    closed: Mapped[bool] = mapped_column(nullable=True)
    date_closed: Mapped[datetime.date] = mapped_column(nullable=True)
    date_open: Mapped[datetime.date] = mapped_column(nullable=True)
    date: Mapped[datetime.date] = mapped_column(nullable=True)


class DataSend(Base):
    __tablename__ = 'datasends'

    date_send: Mapped[date] = mapped_column(unique=True)
    count_all_ill: Mapped[int]
    count_all: Mapped[int]
    count_class_closed: Mapped[int]
    count_ill_closed: Mapped[int]
    count_all_closed: Mapped[int]
    sending: Mapped[bool]
