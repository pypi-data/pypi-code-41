import json

from django.urls import reverse
from django.views.generic import TemplateView

from kitchensink.conf import settings as app_settings
from kitchensink.models import ArchieDoc, Sheet, Project
from kitchensink.utils.auth import secure


@secure
class Home(TemplateView):
    template_name = "kitchensink/home.html"

    def get_sheets_and_docs(self):
        sheets = [sheet.serialize() for sheet in Sheet.objects.all()]
        docs = [doc.serialize() for doc in ArchieDoc.objects.all()]
        return json.dumps(sheets + docs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DOMAIN"] = app_settings.PUBLISH_DOMAIN
        context["SECRET"] = app_settings.SECRET_KEY
        context["PROJECTS"] = self.get_sheets_and_docs()
        context["SHEETS"] = json.dumps(
            [
                {
                    "id": sheet.sheet_id,
                    "title": sheet.title,
                    "publish": reverse("kitchensink-publish-sheet", args=[sheet.id]),
                }
                for sheet in Sheet.objects.order_by("title")
            ]
        )
        context["ARCHIEDOCS"] = json.dumps(
            [
                {
                    "id": doc.doc_id,
                    "title": doc.title,
                    "publish": reverse("kitchensink-publish-archie-doc", args=[doc.id]),
                }
                for doc in ArchieDoc.objects.order_by("title")
            ]
        )
        return context
