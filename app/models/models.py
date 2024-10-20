from sqlalchemy import MetaData, String, Integer, Date, Boolean, Table, Column, JSON, TIMESTAMP, ForeignKey

metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('login', String, nullable=False, unique=True),
    Column('password', String, nullable=False, unique=True),
)

dishes = Table(
    'dishes',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String, nullable=False),
    Column('recipe', Integer, unique=True),
    Column('out', Integer),
    Column('price', Integer),
    Column('prop_dish', JSON),
)

menus = Table(
    'menus',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('date', TIMESTAMP, nullable=False),
    Column('type', String, nullable=False),
    Column('category', String),
    Column('dish_id', Integer, ForeignKey('dishes.id')),
)
