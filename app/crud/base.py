from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseCRUD:
    model = None

    @classmethod
    async def add(cls, session: AsyncSession, **value):
        new = cls.model(**value)
        session.add(new)
        try:
            await session.commit()
        except SQLAlchemyError as error:
            await session.rollback()
            raise error
        return new

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        records = result.scalars().all()
        return records