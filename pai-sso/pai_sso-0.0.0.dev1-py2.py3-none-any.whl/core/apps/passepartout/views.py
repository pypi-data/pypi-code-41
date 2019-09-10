import logging
from urllib.parse import urlparse, urlencode

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect

from ..devices.models import Device
from ..services.models import Service
from ...backend.functions import set_cookie, invalidate_cookie

from .models import Passepartout

logger = logging.getLogger('passepartout')

def get_base_url(full_url):
    parsed_url = urlparse(full_url)
    return_url = parsed_url.scheme + '://' + parsed_url.hostname
    if parsed_url.port is not None:
        return_url += ':' + str(parsed_url.port)
    logger.info('GETTING BASE URL for {0}: {1}'.format(full_url, return_url))
    return return_url

def get_referrer(request):
    referrer = request.META.get('HTTP_REFERER', None)
    if referrer is None:
        _index_previous_should_be = settings.SSO_DOMAINS_DICT[settings.APP_DOMAIN] - 1
        if _index_previous_should_be < 0:
            _last_sso_instance = settings.SSO_DOMAINS[-1]
            if _last_sso_instance == settings.APP_DOMAIN:
                raise Exception('Passepartout Referrer not set')
            else:
                referrer = settings.SSO_FULL_URLS_CHAIN[-1]
                logger.warning('Referrer was empty, setting as LAST SSO instance: {}'.format(referrer))
        else:
            referrer = settings.SSO_FULL_URLS_CHAIN[_index_previous_should_be]
            logger.warning('Referrer was empty, setting as PREVIOUS SSO instance: {}'.format(referrer))
    else:
        logger.debug('COMES FROM referrer: {}'.format(referrer))
    return referrer

def passepartout_login_view(request, token):
    """
    Receives unguessable token by path parameter and destination url by get parameter.
    1) checks user subscription to destination service (obtained by next param as Service url)
    2) checks its position in SSO_URLS ordered dictionary
    3) redirects to next APP_URL if there are subsquent sso domains or directly to service url (if redirecting to APP_URL request will include a jwt token COOKIES)
    """
    try:
        nextUrl = request.GET.get('next', None)
        logger.debug('ENTERING passepartout with next {}'.format(nextUrl))

        if nextUrl is None:
            raise Http404("No next url")

        try:
            passepartout = Passepartout.objects.get(deleted=False, token=token)
        except Passepartout.DoesNotExist:
            raise Http404("Passepartout not found")

        user = passepartout.device.user
        
        next_url_base_path = get_base_url(nextUrl)
        
        service = None
        if next_url_base_path not in settings.SSO_FULL_URLS_CHAIN:
            try:
                service = Service.objects.get(url=next_url_base_path)
            except Service.DoesNotExist:
                raise Http404("Service not found")

        referrer = get_referrer(request)

        comes_from = get_base_url(referrer)
        sso_urls_chain = settings.SSO_URLS_CHAIN
        sso_urls_chain_dict = settings.SSO_URLS_CHAIN_DICT
        logger.info('Passepartout chain dict: {0}, this is: {1}. Comes from {2} with nextUrl: {3}'.format(sso_urls_chain, settings.APP_URL, comes_from, nextUrl))
        
        previous_sso_instance_index = sso_urls_chain_dict[comes_from]
        last_sso_instance_index = len(sso_urls_chain) - 1
        next_sso_instance_index = None

        is_last_bump = previous_sso_instance_index == last_sso_instance_index
        goes_to = None
        redirect_args = None
        
        if is_last_bump:
            logger.info('Is last login bump')
            passepartout.deleted = True
            passepartout.save()
            goes_to = nextUrl
        else:
            redirect_args = {
                'next': nextUrl
            }
            next_sso_instance_index = last_sso_instance_index + 1
            goes_to = sso_urls_chain[next_sso_instance_index]
        
        #if subscribed is None:
        #    subscrition_created = user.subscribe_to_service(service)
        #    logger.info('Did passepartout subscribed user, {0} to {2}? {3}'.format(user, nextUrl, subscription_created))
        #    redirect_args['subscribed'] = 'true'

        formatted_redirect_args = ''
        if not is_last_bump:
            formatted_redirect_args = '?' + urlencode(redirect_args)

        redirect_to = goes_to + formatted_redirect_args
        logger.info('Passepartout login redirecting to {0}'.format(redirect_to))

        response = redirect(redirect_to)

        jwt_token = passepartout.jwt
        set_cookie(response, 'jwt', jwt_token, None)
    except Exception as e:
        logger.error('Passepartout login ERROR: {}'.format(e), exc_info=True)
        raise

    return response

def passepartout_logout_view(request, device_id):
    """
    Logout from all sso_urls_chain, can be called from protected service.
    """
    try:
        nextUrl = request.GET.get('next', None)
        if nextUrl is None:
            raise Http404("No next url")

        referrer = get_referrer(request)

        comes_from = get_base_url(referrer)
        sso_urls_chain = settings.SSO_URLS_CHAIN
        sso_urls_chain_dict = settings.SSO_URLS_CHAIN_DICT
        logger.info('Passepartout chain dict: {0}, this is: {1}. Comes from {2}'.format(sso_urls_chain, settings.APP_URL, comes_from))
        
        last_sso_instance_index = len(sso_urls_chain) - 1
        next_sso_instance_index = 0
        comes_from_sso_instance = False
        previous_sso_instance_index = 0
        is_last_bump = False
        
        try:
            previous_sso_instance_index = sso_urls_chain_dict[comes_from]
            next_sso_instance_index = previous_sso_instance_index + 1
            comes_from_sso_instance = True
            logger.info('Comes from sso instance, previous index: {0}, next index {1}'.format(previous_sso_instance_index, next_sso_instance_index))
        except KeyError:
            logger.info('Comes from protected service')
            pass
        
        # if coming from sso instance looks for next instances or is_last_bump
        if comes_from_sso_instance:
            is_last_bump = next_sso_instance_index >= last_sso_instance_index
        # if coming from protexted service looks for next sso instances or is_last_bump
        else:
            is_last_bump = next_sso_instance_index == last_sso_instance_index

        goes_to = None
        redirect_args = None
        
        if is_last_bump:
            goes_to = nextUrl
            logger.info('Is last logout bump, goes to {}'.format(goes_to))
        else:
            redirect_args = {
                'next': nextUrl
            }
            next_sso_instance_index = last_sso_instance_index + 1
            goes_to = sso_urls_chain[next_sso_instance_index]
            logger.info('Is median logout bump, goes to {}'.format(goes_to))

        formatted_redirect_args = ''
        if not is_last_bump:
            formatted_redirect_args = '?' + urlencode(redirect_args)

        redirect_to = goes_to + formatted_redirect_args
        logger.info('Passepartout logout redirecting to {0}'.format(redirect_to))

        response = redirect(redirect_to)

        if is_last_bump:
            try:
                device = Device.objects.get(id=device_id)
            except Device.DoesNotExist:
                raise Http404("Device not found")
            logger.info('Passepartout deleting device {0} on last bump.'.format(device))
            device.delete()

        invalidate_cookie(response)

    except Exception as e:
        logger.error('Passepartout logout ERROR: {}'.format(e), exc_info=True)
        raise

    return response

