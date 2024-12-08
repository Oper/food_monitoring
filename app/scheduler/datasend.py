import socket
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from venv import logger

from datetime import date

import aiosmtplib
from sqlalchemy.ext.asyncio import AsyncSession

import app.config as config
from app.schemas.datasend import DataSendPydanticDay, DataSendPydanticUpdate, DataSendPydanticAdd, \
    DataSendPydanticAddSending
from app.crud.crud import DataSendCRUD
from app.crud.crud import ClassCRUD
from app.db import session_manager


@session_manager.connection()
async def add_datasend(session: AsyncSession):
    current_date = date.today()
    current_time = time.localtime()
    cure_time = str(current_time.tm_hour).rjust(2, '0') + ':' + str(current_time.tm_min).rjust(2, '0')
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
            # Prepare Message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Мониторинг на ' + current_date.isoformat() + ' время - ' + cure_time
            msg['From'] = config.USER_MAIL
            msg['To'] = config.TO_MAIL
            text = 'Здравствуйте!\nКоличество болеющих обучающихся ВСЕГО: ' + str(
                count_all_ill) + '\nКоличество классов (групп), закрытых на карантин : ' + str(
                count_class_closed) + '\nКоличество болеющих в закрытых классах (группах): ' + str(
                count_ill_closed) + '\nКоличество обучающихся всего в закрытых классах (группах): ' + str(
                count_all_closed)
            msg.attach(MIMEText(text, 'plain', 'utf-8'))

            # Contact SMTP server and send Message
            host = config.HOST_MAIL
            port = config.PORT_MAIL

            smtp = aiosmtplib.SMTP(hostname=host, port=port, start_tls=False, use_tls=True)

            if not data_send_day.sending and current_time.tm_hour == 9 and (
                    50 < current_time.tm_min < 59) and (0 < current_date.isoweekday() < 6):
                await smtp.connect()
                await smtp.login(config.USER_MAIL, config.PASSWORD_MAIL)
                await smtp.send_message(msg)
                await smtp.quit()
                await DataSendCRUD.update(session=session, filters=DataSendPydanticDay(date_send=current_date),
                                          values=DataSendPydanticAddSending(sending=True))
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
    except socket.error as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
