from ..models import ProviderRequest, Provider, User, License


def create(session, license_id, provider_id, endpoint, price_ex, meta_data=dict, user_id=None):

    platform_request = ProviderRequest(
        license_id=license_id,
        provider_id=provider_id,
        user_id=user_id,
        endpoint=endpoint,
        meta_data=meta_data,
        price_ex=price_ex
    )

    session.add(platform_request)
    session.flush()
    session.commit()

    return True


def register_request(session, endpoint, license_id, provider_id=None, user_id=None, meta_data=None):

    # Make sure the provider exists first if we have one. We'll double check a little later
    # to ensure the license and provider match.
    if meta_data is None:
        meta_data = {}

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
