from typing import Optional, List

from pydantic import ConfigDict, BaseModel
from datetime import date


class MenuPydantic(BaseModel):
    date_menu: date
    type_menu: str
    category_menu: str
    dish_id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class MenuPydanticListIn(BaseModel):
    date_menu: date
    type_menu: str
    category_menu: str
    dishs_ids: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class MenuPydanticEdit(BaseModel):
    id: int
