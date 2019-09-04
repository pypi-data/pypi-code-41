from ..models import Provider, License, ProviderRequest, User
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


def register_request(session, endpoint, license_id, provider_id=None, user_id=None, meta_data=dict):

    # Make sure the provider exists first if we have one. We'll double check a little later
    # to ensure the license and provider match.
    if provider_id is not None:
        try:
            provider = session.query(Provider).get(provider_id)
        except Exception as e:
            raise e

        if provider.license_id != license_id:
            raise Exception('Supplied license and provider do not match.')

    if license_id is not None:
        license_count = session.query(License).count(license_id)

        if license_count == 0:
            raise Exception('License does not exist')

    if user_id is not None:
        user_license_count = session.query(User).filter_by(
            User.user_id == user_id,
            User.license_id == license_id
        ).count()

        if user_license_count == 0:
            raise Exception('User is not associated with the supplied license.')

    request = ProviderRequest(
        license_id=license_id,
        provider_id=provider_id,
        user_id=user_id,
        endpoint=endpoint,
        meta_data=meta_data
    )

    session.add(request)
    session.flush()
    session.commit()

    return True
