import uuid
from django.urls import reverse
from django.db import models


class Sheet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "Project",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="sheets",
    )
    title = models.CharField(
        "Project title", max_length=250, help_text="A title for this sheet"
    )
    sheet_id = models.SlugField("Google Sheet ID", help_text="Sheet ID from URL")

    def serialize(self):
        return {
            "id": self.sheet_id,
            "title": self.title,
            "publish": reverse("kitchensink-publish-sheet", args=[self.id]),
            "type": "sheet",
            "project": self.project.title if self.project else None,
        }

    def __str__(self):
        return self.title
