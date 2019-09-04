from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .models import License, Provider, User


DATABASE_URL = "postgresql+psycopg2://{user}:{password}@{host}/{database}".format(
    user=environ.get('CMPL_POSTGRES_USER'),
    password=environ.get('CMPL_POSTGRES_PASSWORD'),
    host=environ.get('CMPL_POSTGRES_HOST'),
    database=environ.get('CMPL_POSTGRES_DB')
)


def get_session():
    engine = create_engine(DATABASE_URL)
    return Session(engine)
