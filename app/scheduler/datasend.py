from venv import logger

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.datasend import DataSendPydanticDay, DataSendPydanticUpdate, DataSendPydanticAdd
from app.crud.crud import DataSendCRUD
from app.crud.crud import ClassCRUD
from app.db import session_manager


@session_manager.connection()
async def add_datasend(session: AsyncSession):
    current_date = date.today()
    count_all_ill = 0
    count_all = 0
    count_class_closed = 0
    count_ill_closed = 0
    count_all_closed = 0

    try:
        all_classes = await ClassCRUD.get_all(session=session)
        if all_classes:
            for _ in all_classes:
                count_all_ill += _.count_ill
                count_all += _.count_class
                if _.closed:
                    count_class_closed += 1
                    count_ill_closed += _.count_ill
                    count_all_closed += _.count_class

        data_send_day = await DataSendCRUD.get_datasend_by_one_day(session=session, day=current_date)
        if data_send_day:
            await DataSendCRUD.update(session=session, filters=DataSendPydanticDay(date_send=current_date),
                                      values=DataSendPydanticUpdate(count_all_ill=count_all_ill, count_all=count_all,
                                                                    count_class_closed=count_class_closed,
                                                                    count_ill_closed=count_ill_closed,
                                                                    count_all_closed=count_all_closed))
        else:
            await DataSendCRUD.add(session=session, values=DataSendPydanticAdd(
                date_send=current_date,
                count_all_ill=count_all_ill,
                count_all=count_all,
                count_class_closed=count_class_closed,
                count_ill_closed=count_ill_closed,
                count_all_closed=count_all_closed,
                sending=False
            ))
    except Exception as e:
        logger.error(e)
