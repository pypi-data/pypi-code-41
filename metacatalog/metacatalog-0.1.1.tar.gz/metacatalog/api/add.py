"""ADD API

The ADD API endpoint can be used to add records to the database.
"""


def _add(session, InstanceModel, **kwargs):
    """
    Common method for inserting a new record. 
    """
    entity = InstanceModel(**kwargs)

    try:
        session.add(entity)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def add_record(session, tablename, **kwargs):
    """
    """
    pass


def add_license():
    pass