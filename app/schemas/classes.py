from pydantic import BaseModel, ConfigDict
from datetime import date


class ClassPydanticIn(BaseModel):
    name_class: str
    man_class: str
    count_class: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ClassPydanticOne(BaseModel):
    name_class: str


class ClassDataPydanticSend(BaseModel):
    name_class: str
    count_ill: int
    closed: bool
    count_day: int
    date: date

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ClassDataPydantic(BaseModel):
    count_ill: int
    proc_ill: int
    closed: bool
    date_closed: date | None
    date_open: date | None
    date: date

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ClassDataPydanticAdd(BaseModel):
    name_class: str
    man_class: str
    count_class: int
    count_ill: int
    proc_ill: int
    closed: bool
    date_closed: date | None
    date_open: date | None
    date: date

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class ClassDataPydanticOpen(BaseModel):
    closed: bool
    date_closed: date | None
    date_open: date | None