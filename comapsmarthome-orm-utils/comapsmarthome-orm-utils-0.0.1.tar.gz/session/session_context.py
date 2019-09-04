from session import session_context
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'postgresql://{}:{}@{}:{}/{}'
    .format(
        os.environ.get('DB_USER', 'postgres'),
        os.environ.get('DB_PASSWORD', 'postgres'),
        os.environ.get('DB_HOST', 'localhost'),
        os.environ.get('DB_PORT', '5432'),
        os.environ.get('DB_NAME', 'postgres')
    )
)
Session = sessionmaker(bind=engine)
session = None


def get_session():
    return session_context.session


def _create_session():
    return Session()


def transactional(func):
    def wrapper(*args):
        if session_context.session is None:
            session_context.session = _create_session()
            try:
                func(*args)
                session_context.session.commit()
            except Exception as e:
                session_context.session.rollback()
                raise e
            finally:
                session_context.session.close()
        else:
            func(*args)

    return wrapper
