from psu_base.classes.Log import Log
from psu_base.services import utility_service
from django.contrib import messages
log = Log()


def post_info(msg):
    return post_message(msg, "info")


def post_success(msg):
    return post_message(msg, "success")


def post_warning(msg):
    return post_message(msg, "warning")


def post_error(msg):
    return post_message(msg, "error")


def post_message(msg, type):
    log.trace(msg)
    request = utility_service.get_request()
    message = str(msg)

    if request is None:
        log.error(f"Request does not exist. Could not post message: {message}")
    else:
        if type == "info":
            messages.info(request, message)
        elif type == "success":
            messages.success(request, message)
        elif type == "warning":
            messages.warning(request, message)
        elif type == "error":
            messages.error(request, message)

    log.end()
    return None
