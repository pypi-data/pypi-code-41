import uuid

from django.urls import reverse
from django.db import models

from foreignform.fields import JSONField


class ArchieDoc(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "Project",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="archie_docs",
    )
    title = models.CharField(
        "Project title", max_length=250, help_text="A title for this doc"
    )
    doc_id = models.SlugField("Google Doc ID", help_text="Doc ID from URL")

    validation_schema = JSONField(blank=True, null=True, help_text="JSON Schema")

    def serialize(self):
        return {
            "id": self.doc_id,
            "title": self.title,
            "publish": reverse("kitchensink-publish-archie-doc", args=[self.id]),
            "type": "doc",
            "project": self.project.title if self.project else None,
        }

    def __str__(self):
        return self.title
