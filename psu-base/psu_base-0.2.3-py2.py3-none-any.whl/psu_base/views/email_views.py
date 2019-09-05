# testing_views.py
#
#   These are views that are used for debugging or testing the status of an app
#

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import generic

from psu_base.classes.Log import Log
from psu_base.classes.Finti import Finti
from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.services import utility_service, email_service, date_service, auth_service
from psu_base.decorators import require_authority
from psu_base.models.email import Email
from django.core.paginator import Paginator
from django.template.loader import render_to_string

log = Log()


@require_authority(['administrator', 'developer'])
def email_list(request):
    """
    Show emails sent from this app
    """
    # Emails sent from this app
    app_code = utility_service.get_app_code()
    app_emails = Email.objects.filter(app_code=app_code)

    # Paginate the results
    paginator = Paginator(app_emails, 50)
    page = request.GET.get('page', 1)
    app_emails = paginator.get_page(page)

    return render(
        request, 'email/list.html',
        {
            'app_emails': app_emails,
        }
    )


@require_authority(['administrator', 'developer'])
def display_email(request):
    """Display one logged email"""
    email_id = request.GET.get('id')
    email_instance = None

    if id:
        email_instance = Email.objects.get(pk=email_id)

    if email_instance:

        # Message content can be displayed from template (html or text) or plain-text content
        message_content = None

        if email_instance.email_template:
            template = email_instance.email_template
            context = eval(email_instance.context) if email_instance.context else {}

            # Try an HTML template
            try:
                message_content = render_to_string(f"{template}.html", context)
            except Exception as ee:
                log.debug("No html template for given email")

            # Try plain-text template
            if not message_content:
                try:
                    message_content = render_to_string(f"{template}.txt", context)
                except Exception as ee:
                    log.debug("No txt template for given email")

        # Use plain-text content
        if not message_content:
            message_content = email_instance.content

        return render(
            request, 'email/instance.html',
            {
                'email_instance': email_instance,
                'message_content': message_content
            }
        )

    else:
        raise Http404('Email not found')


@require_authority(['administrator', 'developer'])
def resend_email(request):
    """Resend one logged email"""
    email_id = request.POST.get('id')
    email_instance = None
    if id:
        log.debug(f"Get email ID: {email_id}")
        email_instance = Email.objects.get(pk=email_id)

    if email_instance:
        log.debug(f"Got email: {email_instance}")
        to = email_instance.get_to_list()
        cc = email_instance.get_cc_list()
        bcc = email_instance.get_bcc_list()
        num_recipients = (len(to) if to else 0) + (len(cc) if cc else 0) + (len(bcc) if bcc else 0)
        email_service.send(
            subject=email_instance.subject,
            content=email_instance.content,
            sender=email_instance.sender,
            to=to,
            cc=cc,
            bcc=bcc,
            email_template=email_instance.email_template,
            context=eval(email_instance.context) if email_instance.context else None,
            test_group_codes=None,
            max_recipients=num_recipients
        )

        return HttpResponse("Message Resent")

    else:
        raise Http404('Email not found')
