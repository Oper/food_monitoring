from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, str_uniq


class User(Base):
    __tablename__ = 'users'

    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )

    password: Mapped[str]