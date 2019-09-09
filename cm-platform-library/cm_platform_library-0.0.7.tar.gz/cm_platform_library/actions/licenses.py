from ..models import License


def get_all(session, offset=0, limit=25):
    return session.query(License) \
        .offset(offset) \
        .limit(limit) \
        .order_by('created_at', 'desc') \
        .all()


def get_by_id(session, license_id):
    return session.query(License).get(license_id)


def create(session, meta_data, flush=True, commit=False):
    license = License(
            meta_data=meta_data
    )

    session.add(license)

    if flush is True:
        session.flush()

    if commit is True:
        session.commit()

    return license
