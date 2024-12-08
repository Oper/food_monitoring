from datetime import date

from pydantic import BaseModel


class DataSendPydanticAdd(BaseModel):
    date_send: date
    count_all_ill: int
    count_all: int
    count_class_closed: int
    count_ill_closed: int
    count_all_closed: int
    sending: bool


class DataSendPydanticUpdate(BaseModel):
    count_all_ill: int
    count_all: int
    count_class_closed: int
    count_ill_closed: int
    count_all_closed: int


class DataSendPydanticDay(BaseModel):
    date_send: date
