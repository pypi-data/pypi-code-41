from django.contrib import admin
from .models import Question, Choice
from mysite.admin import site
from django.contrib.auth.models import User, Group
# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Question', {
            "fields": (
                ['question_text']
            ),
            "classes": (
                ['collapse']
            )
        }),
        ('Date information', {
            "fields": (
                ['pub_date']
            )
        })
    )
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['question_text', 'pub_date']
    search_fields = ['question_text']
    #: default pagination is 100 items per page
    list_per_page = 1
    inlines = [ChoiceInline]
    
site.register(User)
site.register(Group)
site.register(Question, QuestionAdmin)
site.register(Choice)
site.site_header = 'aslknd'
site.site_title = 'abcxyzs'