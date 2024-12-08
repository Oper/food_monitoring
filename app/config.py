from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')

HOST_MAIL = os.environ.get('HOST_MAIL')
PORT_MAIL = os.environ.get('PORT_MAIL')
USER_MAIL = os.environ.get('USER_MAIL')
PASSWORD_MAIL= os.environ.get('PASSWORD_MAIL')
TO_MAIL = os.environ.get('TO_MAIL')

def get_link_db(driver: str) -> str:
    """
    using your DB
    :param driver: postgresql+asyncpg, sqlite+aiosqlite, mysql
    :return:
    """
    return f'{driver}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
