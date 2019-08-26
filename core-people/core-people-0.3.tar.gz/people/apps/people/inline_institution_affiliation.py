from people.models import InstitutionAffiliation
from pyforms_web.widgets.django import ModelAdminWidget


class InstitutionAffiliationInline(ModelAdminWidget):

    MODEL = InstitutionAffiliation
    TITLE = 'Affiliation'

    LIST_DISPLAY = ['institution', 'date_joined', 'date_left']

    FIELDSETS = [
        ('institution', 'date_joined', 'date_left')
    ]

