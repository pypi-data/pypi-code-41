import json
import threading
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from .event import push_view_data


class EventMiddleware(MiddlewareMixin):
	def process_exception(self, request, exception):
		if settings.DEBUG:
			print(exception.__class__.__name__)
			print(exception.message)
		return None


    def process_view(self, request, view_func, view_args, view_kwargs):
		self.fname = view_func.__name__


	def process_response(self, request, response):
		request_data = request.POST.dict() or request.GET.dict()
        try:
		    response_data = json.dumps(response.data, ensure_ascii=False)
        except:
            response_data = response.data

		t = threading.Thread(target=push_view_data, kwargs={
            "method": request.method,
            "path": request.path,
            "request_data": request_data,
            "response_data": response_data,
            "groups": ""
        })
		t.start()
		t.join()
		return response