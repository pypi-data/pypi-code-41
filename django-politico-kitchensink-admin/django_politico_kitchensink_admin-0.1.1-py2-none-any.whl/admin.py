from django.contrib import admin

from kitchensink.models import ArchieDoc, Sheet, Project

admin.site.register(Sheet)
admin.site.register(ArchieDoc)
admin.site.register(Project)
