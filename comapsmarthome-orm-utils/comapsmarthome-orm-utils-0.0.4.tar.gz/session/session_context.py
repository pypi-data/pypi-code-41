import logging
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
            logging.getLogger().debug('Initializing new session object')
            ongoing_session = _create_session()
            session_context.session = ongoing_session
            logging.getLogger().debug('Initialized new session object %s', ongoing_session)
            try:
                func_response = func(*args)
                ongoing_session.commit()
                logging.getLogger().debug('Session %s committed', ongoing_session)
                return func_response
            except:
                ongoing_session.rollback()
                raise
            finally:
                ongoing_session.close()
                session_context.session = None
        else:
            return func(*args)

    return wrapper
