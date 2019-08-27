from zappa.async import run as zappa_run
from django.conf import settings

def log_exception(name, description, trb=None):
	event = Event(settings.SYSTEM_EVENT_TOKEN, settings.SYSTEM_EVENT_NAME, settings.SYSTEM_EVENT_URL)
	event.check_em_notifire(settings)
	return event.log_exception(name, description, trb=trb)


def run(function, **kwargs):
    def wrapper(**kwargs):
        if "kwargs" in kwargs:
            kwargs = kwargs['kwargs']
        return function(**kwargs)
    if settings.DEBUG:
        return wrapper(**kwargs)
    zappa_run(wrapper, kwargs=kwargs)
    return True