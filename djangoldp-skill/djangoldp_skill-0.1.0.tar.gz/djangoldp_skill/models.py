from django.conf import settings
from django.db import models

from djangoldp.models import Model

class Skill(Model):
    name = models.CharField(max_length=255, default='')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="skills")

    class Meta:
        serializer_fields=["@id", "name"]
        nested_fields=[]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add', 'change', 'delete']
        container_path = 'skills/'
        rdf_type = 'hd:skill'


    def __str__(self):
        return self.name
