from pydantic import BaseModel, ConfigDict


class DishPydanticIn(BaseModel):
    title: str
    recipe: int
    out_gramm: int
    price: float
    calories: float
    protein: float
    fats: float
    carb: float
    section: str

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DishPydanticEdit(BaseModel):
    id: int


class DishPydanticTitle(BaseModel):
    title: str
