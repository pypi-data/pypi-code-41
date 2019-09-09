from django.shortcuts import redirect
from psu_base.services import utility_service
from psu_base.classes.Log import Log
from django.http import HttpResponseForbidden

log = Log()


def xss_prevention(get_response):
    def script_response(param, value, is_ajax):
        log.trace([param])

        # Log the suspicious parameter
        log.error(f"Potential XSS attempt in '{param}' parameter")
        log.info(f"\n{value}\n")

        # ToDo: Store attempt in database.
        # ToDo: Lock user out of all psu-enabled Django sites after 3 attempts.

        if is_ajax:
            # Return as failure for AJAX calls
            # ToDo: Generate a "flash message" to display on the view
            return HttpResponseForbidden()
        else:
            # Redirect to "suspicious input" page for non-AJAX requests
            # ToDo: Create a landing page for XSS interceptor
            return redirect('/')

    def xss_middleware(request):
        is_ajax = request.is_ajax()
        log.trace(['AJAX' if is_ajax else 'non-AJAX'])

        for param, value in request.GET.items():
            if utility_service.contains_script(value):
                return script_response(param, value, is_ajax)

        for param, value in request.POST.items():
            if utility_service.contains_script(value):
                return script_response(param, value, is_ajax)

        # Otherwise, continue normally (and add XSS-Protection header)
        response = get_response(request)
        response['X-XSS-Protection'] = "1"
        return response

    return xss_middleware
