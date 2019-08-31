# Create your views here.
import os

from django.conf import settings
from django.views.generic import TemplateView


class ChangelogView(TemplateView):
    template_name = "changelog.html"

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        changelog_path = os.path.join(settings.BASE_DIR, 'CHANGELOG.md')
        if not os.path.exists(changelog_path):
            return {"error": "No changelog"}

        with open(changelog_path) as fd:
            content = fd.read()
        kwargs["data"] = content
        return kwargs
