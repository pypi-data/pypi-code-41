from ..models import ProviderRequest, Provider, User, License


def register_request(session, endpoint, license_id, price_ex, provider_id=None, user_id=None, meta_data=None):

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
        license_count = session.query(License).filter(
            License.license_id == license_id
        ).count()

        if license_count == 0:
            raise Exception('License does not exist')

    if user_id is not None:
        user_license_count = session.query(User).filter(
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
        price_ex=price_ex,
        meta_data=meta_data
    )

    session.add(request)
    session.flush()
    session.commit()

    return True
