import datetime
from datetime import date, timedelta
from typing import Annotated
from venv import logger

from fastapi.routing import APIRouter
from fastapi import Request, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import app.config as config
from app.db import SessionDep
from app.crud.crud import ClassCRUD, DataSendCRUD
from app.schemas.classes import ClassPydanticIn, ClassPydanticOne, ClassDataPydanticAdd, ClassDataPydanticSend, \
    ClassDataPydantic, ClassDataPydanticOpen, ClassDataPydanticClosed
from app.auth.dependencies import get_current_user
from app.auth.models import User

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix='/monitoring', tags=['sanmon'])


@router.get('/', response_class=HTMLResponse)
async def monitoring(request: Request, session: AsyncSession = SessionDep):
    title = 'Санитарно-эпидемиологическая обстановка в Школе'

    current_date = date.today()
    classes_list: dict = {}

    count_all_ill = 0
    count_all = 0

    try:
        all_classes = await ClassCRUD.get_all(session=session)
        if all_classes:
            count = 1
            for _class in all_classes:
                if len(_class.name_class) == 2:
                    count_all += _class.count_class
                    count_all_ill += _class.count_ill
                    if _class.name_class not in classes_list:
                        classes_list[_class.name_class] = []
                    classes_list[_class.name_class].append({
                        'id': count,
                        'man_class': _class.man_class,
                        'count_ill': _class.count_ill,
                        'count_class': _class.count_class,
                        'proc_ill': _class.proc_ill,
                        'closed': _class.closed,
                        'date_closed': _class.date_closed,
                        'date_open': _class.date_open,
                        'date': _class.date
                    })
                    count += 1
            for count_id, _class in enumerate(all_classes, start=count):
                if len(_class.name_class) == 3:
                    count_all += _class.count_class
                    count_all_ill += _class.count_ill
                    if _class.name_class not in classes_list:
                        classes_list[_class.name_class] = []
                    classes_list[_class.name_class].append({
                        'id': count_id,
                        'man_class': _class.man_class,
                        'count_ill': _class.count_ill,
                        'count_class': _class.count_class,
                        'proc_ill': _class.proc_ill,
                        'closed': _class.closed,
                        'date_closed': _class.date_closed,
                        'date_open': _class.date_open,
                        'date': _class.date
                    })
    except Exception as e:
        logger.error(e)

    proc_all = 0 if count_all_ill == 0 else round(count_all_ill * 100 / count_all)

    send_status = False
    try:
        sending_mail_data = await DataSendCRUD.get_sends_status_by_from_date(session=session, day=current_date)
        if sending_mail_data:
            send_status = sending_mail_data.sending
    except Exception as e:
        logger.error(e)
    status = f'Данные на {current_date.isoformat()} отправлены в Cектор' if send_status else 'Данные не отправлены в сектор'
    full_status = 'd-inline-flex mb-3 px-2 py-1 fw-semibold text-success-emphasis bg-success-subtle border border-success rounded-2' if send_status else 'd-inline-flex mb-3 px-2 py-1 fw-semibold text-success-emphasis bg-secondary-subtle border border-danger rounded-2'

    return templates.TemplateResponse(request=request, name='monitoring.html',
                                      context={'title': title, 'title_school': config.SCHOOL,
                                               'date_current': current_date,
                                               'count_all_ill': count_all_ill, 'count_all': count_all,
                                               'proc_all': proc_all, 'send_status': status, 'classes': classes_list,
                                               'full_status': full_status})


@router.post('/create_class/')
async def create_class(request: Request, data: Annotated[ClassPydanticIn, Form()],
                       user_data: User = Depends(get_current_user), session: AsyncSession = SessionDep):
    name_class = data.name_class
    man_class = data.man_class
    count_class = data.count_class
    try:
        current_class = await ClassCRUD.get_class_by_one(session=session, name_class=name_class)
        if current_class:
            values = data.model_dump()
            await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                   values=ClassPydanticIn(**values))
        else:
            await ClassCRUD.add(session=session,
                                values=ClassDataPydanticAdd(
                                    name_class=name_class,
                                    man_class=man_class,
                                    count_class=count_class,
                                    count_ill=0,
                                    proc_ill=0,
                                    closed=False,
                                    date_open=None,
                                    date_closed=None,
                                    date=date.today()))
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin_monitoring').include_query_params(msg="Successfully created!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/del_class/')
async def del_class(request: Request, data: Annotated[ClassPydanticOne, Form()],
                    user_data: User = Depends(get_current_user), session: AsyncSession = SessionDep):
    name_class = data.name_class
    try:
        await ClassCRUD.delete(session=session, filters=ClassPydanticOne(name_class=name_class))
    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('admin_monitoring').include_query_params(msg="Successfully deleted!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/closing_class/')
async def del_class(request: Request, data: Annotated[ClassDataPydanticClosed, Form()],
                    user_data: User = Depends(get_current_user), session: AsyncSession = SessionDep):
    name_class = data.name_class
    closed = data.closed
    date_closed = data.date_closed
    date_open = data.date_open
    print(date_open, date_closed)
    try:
        await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                               values=ClassDataPydanticOpen(closed=closed, date_closed=date_closed,
                                                            date_open=date_open))
    except Exception as e:
        logger.error(e)
        redirect_url = request.url_for('404').include_query_params(msg='ERROR closing class!')
        return RedirectResponse(redirect_url, status_code=status.HTTP_304_NOT_MODIFIED)
    redirect_url = request.url_for('admin_monitoring').include_query_params(msg='Successfully closed!')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/send_data_class')
async def send_data_class(request: Request, data: Annotated[ClassDataPydanticSend, Form()],
                          session: AsyncSession = SessionDep):
    name_class = data.name_class
    count_ill = data.count_ill
    date_send = date.today()
    count_day = data.count_day
    closed = data.closed

    try:
        current_class = await ClassCRUD.get_class_by_one(session=session, name_class=name_class)
        proc_ill = 0 if count_ill == 0 else round(count_ill * 100 / current_class.count_class)
        if current_class:
            if current_class.closed and closed:
                await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                       values=ClassDataPydantic(
                                           count_ill=count_ill,
                                           proc_ill=proc_ill,
                                           closed=closed,
                                           date=date_send,
                                           date_open=current_class.date_open,
                                           date_closed=current_class.date_closed
                                       ))
            elif current_class.closed and not closed:
                await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                       values=ClassDataPydantic(
                                           count_ill=count_ill,
                                           proc_ill=proc_ill,
                                           closed=False,
                                           date=date_send,
                                           date_open=None,
                                           date_closed=None
                                       ))
            elif closed and proc_ill > 20:
                await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                       values=ClassDataPydantic(
                                           count_ill=count_ill,
                                           proc_ill=proc_ill,
                                           closed=True,
                                           date=date_send,
                                           date_open=date_send + timedelta(days=count_day),
                                           date_closed=date_send + timedelta(days=1)
                                       ))
            else:
                await ClassCRUD.update(session=session, filters=ClassPydanticOne(name_class=name_class),
                                       values=ClassDataPydantic(
                                           count_ill=count_ill,
                                           proc_ill=proc_ill,
                                           closed=False,
                                           date=date_send,
                                           date_open=None,
                                           date_closed=None
                                       ))

    except Exception as e:
        logger.error(e)
    redirect_url = request.url_for('monitoring').include_query_params(msg="Successfully send data!")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get('/admin', response_class=HTMLResponse)
async def admin_monitoring(request: Request, user_data: User = Depends(get_current_user),
                           session: AsyncSession = SessionDep):
    title = 'Панель управления классами'

    classes_list: dict = {}

    try:
        all_classes = await ClassCRUD.get_all(session=session)
        if all_classes:
            for count_id, _class in enumerate(all_classes, start=1):
                if _class.name_class not in classes_list:
                    classes_list[_class.name_class] = []
                classes_list[_class.name_class].append({
                    'id': count_id,
                    'man_class': _class.man_class,
                    'count_ill': _class.count_ill,
                    'count_class': _class.count_class,
                    'proc_ill': _class.proc_ill,
                    'closed': _class.closed,
                    'date_closed': _class.date_closed,
                    'date_open': _class.date_open,
                    'date': _class.date
                })
    except Exception as e:
        logger.error(e)

    return templates.TemplateResponse(request=request, name='admin_monitoring.html',
                                      context={'title': title, 'title_school': config.SCHOOL,
                                               'date_current': datetime.date.today(), 'classes': classes_list})


@router.get('/analysis', response_class=HTMLResponse)
async def analysis(request: Request, session: AsyncSession = SessionDep):
    title = 'Анализ заболеваемости'
    json_data: dict = {}
    labels = []
    data = []
    data_class_closed = []
    try:
        datasend_by_30 = await DataSendCRUD.get_last_by_30(session=session)
        for datasend in datasend_by_30:
            labels.append(datasend.date_send.isoformat())
            data.append(datasend.count_all_ill)
            data_class_closed.append(datasend.count_class_closed)

        for count, datasend in enumerate(datasend_by_30, start=1):
            if datasend.date_send not in json_data:
                json_data[datasend.date_send] = []
            json_data[datasend.date_send].append({
                'id': count,
                'count_all_ill': datasend.count_all_ill,
                'count_class_closed': datasend.count_class_closed
            })
    except Exception as e:
        logger.error(e)

    return templates.TemplateResponse(request=request, name='analysis.html',
                                      context={'title': title, 'title_school': config.SCHOOL,
                                               'date_current': datetime.date.today(), 'json_data': json_data,
                                               'labels': labels, 'data': data,
                                               'data_class_closed': data_class_closed})
