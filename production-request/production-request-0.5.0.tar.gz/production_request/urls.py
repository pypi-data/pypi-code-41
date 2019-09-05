from django.conf.urls import (
    url,
)

from production_request.views import (
    save_client_log,
)

production_request_url = url(r'^production-request', save_client_log)