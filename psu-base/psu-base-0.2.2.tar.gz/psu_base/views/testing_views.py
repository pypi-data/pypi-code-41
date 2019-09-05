# testing_views.py
#
#   These are views that are used for debugging or testing the status of an app
#

from django.shortcuts import render, redirect
from django.http import JsonResponse
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


log = Log()


def test_status(request):
    """
    The test page that DAP will view to ensure the app has been deployed with the correct
    version and local setting/configuration values. Obvious incorrect settings should be flagged.
    """
    # Settings as a dict so they can be rendered in the view
    configs = {}
    for ss in dir(settings):
        configs[ss] = settings.__getattr__(ss)

    # Settings that will be evaluated per environment
    env = configs['ENVIRONMENT']
    cas = configs['CAS_URL']
    finti = configs['FINTI_URL']

    # Finti SSO-Proxy data (to show working connection to Finti)
    sso_proxy = Finti().get('wdt/v1/sso_proxy/status', include_metadata=True)
    # Get the SID of the connected database, or an error message if not connected
    sid = sso_proxy['message'] if sso_proxy['message'] and len(sso_proxy['message']) < 6 else None
    sid_message = sso_proxy['message'] if sso_proxy['message'] and not sid else None

    # Session Duration/Expiration/Timeout
    session_data = {
        'expiry_seconds': request.session.get_expiry_age(),
        'expiry_description': date_service.seconds_to_duration_description(request.session.get_expiry_age())
    }

    # Server time
    server_time = ConvenientDate('now')
    my_time_time = ConvenientDate('08/26/2019 13:28')

    # Flag any obvious issues
    issues = []
    if env == 'PROD':
        if 'https://sso.pdx.edu' not in cas:
            issues.append('cas')
        if 'https://ws.oit.pdx.edu' not in finti:
            issues.append('finti')
        if sid != 'OPRD':
            issues.append('sid')
        if sid_message:
            issues.append('sid_message')
    # In non-production...
    else:
        # Should not use prod Finti
        if 'https://ws.oit.pdx.edu' in finti:
            issues.append('finti')
        if sid == 'OPRD':
            issues.append('sid')
        if sid_message:
            issues.append('sid_message')

    return render(
        request, 'test/status.html',
        {
            'configs': configs,
            'session_data': session_data,
            'sso_proxy': sso_proxy,
            'issues': issues,
            'cas': cas,
            'finti': finti,
            'sid': sid,
            'sid_message': sid_message,
            'server_time': server_time, 'my_time_time': my_time_time,
        }
    )


@require_authority('developer')
def test_session(request):
    """
    Display the contents of the session
    """

    contents = {}
    for kk in list(request.session.keys()):
        contents[kk] = request.session.get(kk)

    expiry_seconds = request.session.get_expiry_age()   # Total time in seconds
    expiry_description = date_service.seconds_to_duration_description(expiry_seconds)

    return render(
        request, 'test/session.html',
        {'contents': contents, 'expiry_description': expiry_description, 'expiry_seconds': expiry_seconds}
    )


def test_versions(request):
    # Get a list of PSU apps in use and their versions
    installed_apps = utility_service.get_installed_plugins()

    # Determine which CAS environment is in use
    cas = utility_service.get_setting('CAS_URL')
    if '-dev' in cas:
        cas_env = 'DEV'
    elif '-stage' in cas:
        cas_env = 'STAGE'
    else:
        cas_env = 'PROD'

    # Determine which Finti environment is in use (if any)
    finti = utility_service.get_setting('FINTI_URL')
    if 'ws-test.oit.pdx.edu' in finti:
        finti_env = 'TEST'
    elif 'ws.oit.pdx.edu' in finti:
        finti_env = 'PROD'
    elif finti:
        finti_env = 'DEV'
    else:
        finti_env = 'NONE'

    model = {
        'app_environment': utility_service.get_setting('ENVIRONMENT'),
        'sso_environment': cas_env,
        'finti': finti_env,
        'app_version': utility_service.get_app_version(),
        'psu_apps': installed_apps
    }
    return JsonResponse(model)


@require_authority('developer')
def email_test_page(request):
    """
    A page to test email features
    """
    # Send a test email if the form was submitted
    if request.method == 'POST' and request.POST.get('to_recipient'):
        recipient = request.POST.get('to_recipient')
        email_service.send(
            subject=f"Test Email From {utility_service.get_app_name()}",
            to=recipient,
            content=f"Greetings from {utility_service.get_app_name()} version {utility_service.get_app_version()}!"
        )
        return redirect('psu:email')

    # Display the list of allowed testers, and the default recipient
    default_recipient = email_service.get_default_recipient()
    testers = email_service.get_testing_emails()

    return render(
        request, 'test/email.html',
        {'default_recipient': default_recipient, 'testers': testers}
    )


@method_decorator(csrf_exempt, name='dispatch')
class FintiView(generic.base.TemplateView):
    """
    A view demonstrating using the PSU_Base Finti class to make Finti API calls
    """
    template_name = 'test/finti.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Is the user allowed to access this?
        authorized = auth_service.has_authority('developer')
        context['authorized'] = authorized
        if not authorized:
            messages.error(self.request, 'You are not authorized to make an API call')
            return context

        finti = Finti()
        log.info("REQUEST.METHOD: {}".format(self.request.method))

        # Get data that may have been submitted
        submitted_path = self.request.GET.get('api_url')
        submitted_token = self.request.GET.get('token')
        submitted_metadata = self.request.GET.get('metadata')
        submitted_http_method = self.request.GET.get('http_method')
        submitted_payload = self.request.GET.get('payload')

        # Pre-populate the form with default or previously submitted values
        context['base_url'] = finti.get_url()
        context['api_path'] = submitted_path if submitted_path else ''
        context['token'] = submitted_token if submitted_token else ''
        context['metadata'] = submitted_metadata if submitted_metadata else False
        context['http_method'] = submitted_http_method if submitted_http_method else 'GET'
        context['payload'] = submitted_payload if submitted_payload else ''

        # Make the API call
        content = {}
        if self.request.GET:
            # If a non-default token was given, it must replace the value from local_settings
            if submitted_token:
                finti.token = submitted_token
            if submitted_http_method:
                messages.info(self.request, "Calling method: {}".format(submitted_http_method.upper()))
                # GET calls
                if submitted_http_method == 'GET':
                    content = finti.get(submitted_path, include_metadata=submitted_metadata)
                # POST calls
                elif submitted_http_method == 'POST':
                    content = finti.post(submitted_path, submitted_payload, include_metadata=submitted_metadata)
                # PUT calls
                elif submitted_http_method == 'PUT':
                    content = finti.put(submitted_path, submitted_payload, include_metadata=submitted_metadata)
                # DELETE calls
                elif submitted_http_method == 'DELETE':
                    content = finti.delete(submitted_path, include_metadata=submitted_metadata)

                if 'status' in content and content['result'] == 'error':
                    messages.error(self.request, "Call returned error: {}".format(content['message']))
            else:
                messages.error(self.request, "No method was chosen!")

        # Save the result to the context (to display on page)
        try:
            context['content'] = content
        except Exception as ee:
            log.warn("Not JSON-able: {}".format(ee))
            context['content'] = content.text

        return context

