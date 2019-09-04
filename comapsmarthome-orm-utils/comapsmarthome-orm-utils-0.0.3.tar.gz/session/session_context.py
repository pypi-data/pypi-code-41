from sqlalchemy.orm import sessionmaker

from session import session_context

Session = sessionmaker()
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
                func_response = func(*args)
                session_context.session.commit()
                return func_response
            except Exception as e:
                session_context.session.rollback()
                raise e
            finally:
                session_context.session.close()
        else:
            return func(*args)

    return wrapper
