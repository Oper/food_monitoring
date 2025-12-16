from contextlib import asynccontextmanager
from datetime import datetime
from functools import wraps
from typing import AsyncGenerator, Annotated, Callable

from fastapi import Depends
from sqlalchemy import Integer, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr, class_mapper
from loguru import logger

from app import config

DATABASE_URL = config.get_link_db('postgresql+asyncpg')

engine = create_async_engine(url=DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

async def create_all_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class DatabaseSessionManager:
    """
    Класс для управления асинхронными сессиями базы данных.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    @asynccontextmanager
    async def create_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Создаёт и предоставляет новую сессию базы данных.
        Гарантирует закрытие сессии по завершении работы.
        """
        async with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Ошибка при создании сессии базы данных: {e}")
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def transaction(self, session: AsyncSession) -> AsyncGenerator[None, None]:
        """
        Управление транзакцией: коммит при успехе, откат при ошибке.
        """
        try:
            yield
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception(f"Ошибка транзакции: {e}")
            raise


    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Зависимость для FastAPI, возвращающая сессию с управлением транзакцией.
        """
        async with self.create_session() as session:
            async with self.transaction(session):
                yield session

    def connection(self):
        """
        Декоратор для управления сессией
        """

        def decorator(method):
            @wraps(method)
            async def wrapper():
                async with self.session_maker() as session:
                    try:
                        result = await method(session=session)
                        await session.commit()
                        return result
                    except Exception as e:
                        await session.rollback()
                        logger.error(f"Ошибка при выполнении транзакции: {e}")
                        raise
                    finally:
                        await session.close()

            return wrapper

        return decorator


    @property
    def transaction_session_dependency(self) -> Callable:
        """Возвращает зависимость для FastAPI с поддержкой транзакций."""
        return Depends(self.get_transaction_session)


session_manager = DatabaseSessionManager(async_session_maker)

# Dependency для использования в маршрутах FastAPI
SessionDep = session_manager.transaction_session_dependency
