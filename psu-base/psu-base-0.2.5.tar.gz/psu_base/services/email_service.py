from psu_base.services import auth_service
from psu_base.services import utility_service
from psu_base.classes.Finti import Finti
from psu_base.classes.Log import Log
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from psu_base.models.email import Email

log = Log()


def get_default_recipient():
    # When authenticated, default to CAS-authenticated user
    if auth_service.is_logged_in():
        return auth_service.get_auth_object().sso_user.email_address

    # When non-authenticated in non-production, allow a default address to be specified and stored in the session
    elif utility_service.is_non_production():
        return utility_service.get_session_var("psu_base_default_recipient")

    # Otherwise, there is no default recipient
    return None


def set_default_email(default_recipient):
    """
    When non-authenticated in non-production, a default recipient can be specified and stored in the session
    (this helps test emails for non-authenticated situations, like Dual Credit Applications)
    """
    utility_service.set_session_var("psu_base_default_recipient", default_recipient)


def get_testing_emails(group_codes=None):
    """
    Get email addresses that are allowed to receive non-production emails.
    If no group code is specified, all allowed emails will be returned.
    Group codes may be a list, or a single group code.
    If OIT is not in your list, it will be added automatically (because OIT always gets emails!)
    """
    log.trace()

    # If a single group code was given, make it a list
    if group_codes and type(group_codes) is not list:
        group_codes = [group_codes]

    # If OIT was not specified, add it automatically
    if type(group_codes) is list and 'OIT' not in group_codes:
        group_codes.append('OIT')

    final_list = []
    try:
        # Get all defined groups
        all_groups = Finti().get('wdt/v1/sso_proxy/test_groups')

        # Get the addresses associated with the specified groups
        for group_dict in all_groups:
            if group_codes is None or group_dict['group_code'] in group_codes:
                final_list.extend(group_dict['email_addresses'])

        # Make the list unique
        final_list = list(set(final_list))

    except Exception as ee:
        log.error(f"Error getting non-prod testing emails: {str(ee)}")

    return final_list


def send(
        subject=None,
        content=None,
        sender=None,
        to=None,
        cc=None,
        bcc=None,
        email_template=None,
        context=None,
        test_group_codes=None,
        max_recipients=10,  # We rarely send an email to more than 10 people. Exceptions should have to specify how many
):
    log.trace([subject])
    invalid = False
    error_message = None

    # If sender not specified, use the default sender address
    if not sender:
        sender = utility_service.get_setting('EMAIL_SENDER')

    # Subject should never be empty.  If it is, log an error and make something up.
    if not subject:
        log.error("Email subject is empty!")
        subject = f"Message from {utility_service.get_app_name()}"

    to, cc, bcc, num_recipients = _prepare_recipients(to, cc, bcc, test_group_codes)

    # Enforce max (and min) recipients
    if num_recipients == 0:
        error_message = f"Email failed validation: No Recipients"
        log.error(error_message)
        invalid = True
    elif num_recipients > max_recipients:
        error_message = f"Email failed validation: Too Many ({num_recipients} of {max_recipients}) Recipients"
        log.error(error_message)
        invalid = True

    # If a template has not been specified, use the base template
    # (Use template=False to not use a template)
    if email_template is None:
        email_template = 'email/base_template'

    # Standard template uses subject as page title (may not even matter?)
    if not context:
        context = {'subject': subject}
    elif 'subject' not in context:
        context['subject'] = subject

    # Standard template will print plain content inside the HTML template
    if content and 'content' not in context:
        context['content'] = content

    # Render the template to a string (HTML and plain text)
    html = plain = None
    try:
        if email_template:
            html = render_to_string(f"{email_template}.html", context)
    except Exception as ee:
        log.error(f"Unable to render template: {email_template}.html")
        log.debug(str(ee))
    try:
        if email_template:
            plain = render_to_string(f"{email_template}.txt", context)
    except Exception as ee:
        if content:
            # Render the content as plain text
            plain = content
        else:
            log.error(f"Unable to render template: {email_template}.txt")
            log.debug(str(ee))

    if invalid:
        log.warning(f"Email was not sent: {subject}")

    else:
        try:
            # Build the email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain,
                from_email=sender,
                to=to,
                cc=cc,
                bcc=bcc
            )

            # If there is an html version, attach it
            if html:
                email.attach_alternative(html, "text/html")

            # Send the email
            email.send()

        except Exception as ee:
            invalid = True
            error_message = str(ee)
            log.warning(f"Error sending email: {error_message}")
            log.warning(f"Email was probably not sent: {subject}")

    # Log the email
    status = 'F' if invalid else 'S'
    _record(
        subject=subject,
        content=content,
        sender=sender,
        to=to,
        cc=cc,
        bcc=bcc,
        email_template=email_template,
        context=context,
        max_recipients=max_recipients,
        status=status,
        error_message=error_message
    )

    return status == 'S'


def _prepare_recipients(to, cc, bcc, test_group_codes):
    """
    Used by send() to prepare the recipients in a unit-testable way
    """
    # Recipients should be in list format
    if type(to) is not list:
        to = [to]
    if type(cc) is not list:
        cc = [cc]
    if type(bcc) is not list:
        bcc = [bcc]

    def clean(address):
        return address.lower().replace('gtest.', '').replace('gdev.', '')

    # Recipient lists should be unique. To assist with this, make all emails lowercase
    to = list(set([clean(address) for address in to if address]))
    cc = list(set([clean(address) for address in cc if address and clean(address) not in to]))
    bcc = list(set([clean(aa) for aa in bcc if aa and clean(aa) not in to and clean(aa) not in cc]))

    # Get the total number of recipients
    num_recipients = len(to) if to else 0
    num_recipients += len(cc) if cc else 0
    num_recipients += len(bcc) if bcc else 0

    # If this is non-production, remove any non-allowed addresses
    if utility_service.is_non_production() and num_recipients > 0:
        testing_emails = get_testing_emails(test_group_codes)
        default_recipient = get_default_recipient()
        allowed_to = [aa for aa in to if aa in testing_emails or aa == default_recipient]
        allowed_cc = [aa for aa in cc if aa in testing_emails or aa == default_recipient]
        allowed_bcc = [aa for aa in bcc if aa in testing_emails or aa == default_recipient]

        # Get the total number of allowed recipients
        num_allowed_recipients = len(allowed_to) if allowed_to else 0
        num_allowed_recipients += len(allowed_cc) if allowed_cc else 0
        num_allowed_recipients += len(allowed_bcc) if allowed_bcc else 0

        if num_allowed_recipients < num_recipients:
            not_allowed = {
                'to': [aa for aa in to if aa not in allowed_to],
                'cc': [aa for aa in cc if aa not in allowed_cc],
                'bcc': [aa for aa in bcc if aa not in allowed_bcc]
            }
            log.info(f"The following recipients were removed from the recipient list:\n{not_allowed}")

        if num_allowed_recipients == 0 and default_recipient:
            log.info(f"No allowed non-prod recipients. Redirecting to {default_recipient}.")
            allowed_to = [default_recipient]
            num_allowed_recipients = 1

        return allowed_to, allowed_cc, allowed_bcc, num_allowed_recipients

    else:
        return to, cc, bcc, num_recipients


def _record(subject, content, sender, to, cc, bcc, email_template, context, max_recipients, status=None, error_message=None):
    """
    Used by send() to record emails with enough data to be able to re-send them later if needed
    """
    log.trace()

    email_instance = Email(
        app_code=utility_service.get_app_code(),
        url=utility_service.get_request().path,
        initiator=auth_service.get_auth_object().sso_user.username if auth_service.is_logged_in() else None,
        status=status,
        error_message=error_message,
        subject=subject,
        content=content, 
        sender=sender, 
        to=str(to) if to else None,
        cc=str(cc) if cc else None,
        bcc=str(bcc) if bcc else None,
        email_template=email_template,
        context=str(context) if context else None,
        max_recipients=max_recipients
    )
    email_instance.save()
