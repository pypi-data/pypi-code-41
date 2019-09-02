from ..models import Provider
from cm_service_library.helpers import generate_uuid_str
from cm_service_library.crypto import hash_secret


def get_all(session, offset=0, limit=25):
    return session.query(Provider) \
        .offset(offset) \
        .limit(limit) \
        .order_by('created_at', 'desc') \
        .all()


def get_by_id(session, license_id):
    return session.query(Provider).get(license_id)


def create(session, license, name, meta_data={}, provider_external_id=None, flush=True, commit=False):
    provider_secret = generate_uuid_str()

    provider = Provider(
        license_id=license.license_id,
        provider_external_id=provider_external_id,
        name=name,
        meta_data=meta_data,
        provider_secret=hash_secret(provider_secret)
    )

    session.add(provider)

    if flush is True:
        session.flush()

    if commit is True:
        session.commit()

    return provider, provider_secret
