import uuid

from django.db import models


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        "Project title",
        max_length=250,
        help_text="A title for this project",
        unique=True,
    )

    def __str__(self):
        return self.title
