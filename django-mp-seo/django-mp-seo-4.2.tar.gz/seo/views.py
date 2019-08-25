
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from seo.models import RedirectRecord, ErrorRecord


def _render_error_page(request, code, message, template_name='error.html'):
    context = {'code': code, 'message': message}
    return render(request, template_name, context, status=code)


def page_not_found(request, **kwargs):

    path = request.path

    try:
        record = RedirectRecord.objects.get(old_path=path)
        return redirect(record.new_path, permanent=True)
    except RedirectRecord.DoesNotExist:
        pass

    if not path.startswith('/static/') and not path.startswith('/media/'):
        ErrorRecord.create(request, 404)

    return _render_error_page(request, 404, _('Page not found'))


def server_error(request, **kwargs):
    return _render_error_page(request, 500, _('Server error'))


def permission_denied(request, **kwargs):
    return _render_error_page(request, 403, _('Permission denied'))


def bad_request(request, **kwargs):
    return _render_error_page(request, 400, _('Bad request'))
