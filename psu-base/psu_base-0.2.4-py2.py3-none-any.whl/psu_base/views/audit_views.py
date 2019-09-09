# testing_views.py
#
#   These are views that are used for debugging or testing the status of an app
#

from django.shortcuts import render
from django.shortcuts import redirect
from psu_base.services import utility_service, auth_service, date_service
from psu_base.decorators import require_authority
from psu_base.models.audit import Audit
from django.db.models import Q
from django.http import HttpResponseNotAllowed, Http404, HttpResponseForbidden, HttpResponse
import re
from psu_base.classes.Log import Log
from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.classes.User import User
from django.core.paginator import Paginator

log = Log()


@require_authority(['oit-es-manager'])
def audit_list(request):
    """
    List audit events
    """
    # Get a list of all audit event codes (for filtering)
    event_codes = Audit.objects.values('event_code').distinct()

    # Initialize filter variables
    ff = {
        'username': None, 'sso': None, 'impersonated': None, 'proxied': None,
        'from_date': None, 'to_date': None,
        'from_date_display': None, 'to_date_display': None,
        'event_code': None,
    }
    user_instance = None

    # Were filters updated/submitted?
    if request.GET.get('filter_submission'):

        # Get user filters
        ff['username'] = request.GET.get('username')
        user_types = request.GET.getlist('user_type')
        if user_types:
            ff['sso'] = 'S' in user_types
            ff['impersonated'] = 'I' in user_types
            ff['proxied'] = 'P' in user_types
        # Provide default user_type if none selected
        if ff['username'] and (not ff['impersonated']) and (not ff['proxied']):
            ff['sso'] = True

        # Get date filters
        ff['from_date'] = request.GET.get('from_date')
        ff['to_date'] = request.GET.get('to_date')

        # Get event filter
        ff['event_code'] = request.GET.getlist('event_code')

        # Save selections for future requests (pagination)
        utility_service.set_session_var('audit_filter_selections', ff)

    # Otherwise, look for saved filters
    else:
        ff = utility_service.get_session_var('audit_filter_selections', ff)

    # Look up user info
    if ff['username']:
        user_instance = User(ff['username'])  # also accepts PSU ID or pidm

    # Get convenient date instances
    from_date_instance = ConvenientDate(ff['from_date'])
    to_date_instance = ConvenientDate(ff['to_date'])

    # Start building the query
    audits = Audit.objects
    filtered = False

    if ff['username']:
        # Get the username. If PSU ID was given, will need to get username from user_instance
        query_user = ff['username'] if user_instance is None else user_instance.username
        if ff['sso']:
            if filtered:
                audits = audits | Audit.objects.filter(Q(username=query_user))
            else:
                audits = Audit.objects.filter(Q(username=query_user))
                filtered = True
        if ff['impersonated']:
            if filtered:
                audits = audits | Audit.objects.filter(Q(impersonated_username=query_user))
            else:
                audits = Audit.objects.filter(Q(impersonated_username=query_user))
                filtered = True
        if ff['proxied']:
            if filtered:
                audits = audits | Audit.objects.filter(Q(proxied_username=query_user))
            else:
                audits = Audit.objects.filter(Q(proxied_username=query_user))
                filtered = True

    if ff['from_date']:
        # Must be in proper timestamp format (with hours and minutes)
        ff['from_date'] = from_date_instance.timestamp()
        if filtered:
            audits = audits & Audit.objects.filter(Q(date_created__gte=ff['from_date']))
        else:
            audits = Audit.objects.filter(Q(date_created__gte=ff['from_date']))
            filtered = True

    if ff['to_date']:
        # Must be in proper timestamp format (with hours and minutes)
        ff['to_date'] = to_date_instance.timestamp()
        if filtered:
            audits = audits & Audit.objects.filter(Q(date_created__lte=ff['to_date']))
        else:
            audits = Audit.objects.filter(Q(date_created__lte=ff['to_date']))
            filtered = True

    if ff['event_code']:
        audits = audits & Audit.objects.filter(Q(event_code__in=ff['event_code']))
        log.info(f"QUERYING FOR EVENT: {ff['event_code']}")
        filtered = True

    if not filtered:
        log.info(f"QUERYING FOR: ALL")
        audits = audits.all()

    audits = audits.order_by('-date_created')

    paginator = Paginator(audits, 50)
    page = request.GET.get('page', 1)
    audits = paginator.get_page(page)

    return render(
        request, 'audit/list.html',
        {
            'audits': audits,
            'ff': ff,
            'user_instance': user_instance,
            'event_codes': {result['event_code']: result['event_code'] for result in event_codes},
            'from_date_instance': from_date_instance, 'to_date_instance': to_date_instance
        }
    )
