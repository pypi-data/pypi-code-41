from try_django.admin import admin_site
from .models import Question, Choice
# Register your models here.

admin_site.register(Question)
admin_site.register(Choice)