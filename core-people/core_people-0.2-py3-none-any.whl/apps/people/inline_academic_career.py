from people.models import AcademicCareer
from pyforms_web.widgets.django import ModelAdminWidget


class AcademicCareerInline(ModelAdminWidget):

    MODEL = AcademicCareer

    LIST_DISPLAY = ['institution', 'degree', 'field_of_study', 'graduation_year']

    FIELDSETS = [
        ('institution', 'degree', 'field_of_study', 'graduation_year')
    ]

