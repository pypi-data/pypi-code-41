from pyforms.basewidget import segment, no_columns
from pyforms_web.widgets.django import ModelFormWidget

from .humanresourses_form import HumanResourcesForm
from .inline_academic_career import AcademicCareerInline
from .inline_institution_affiliation import InstitutionAffiliationInline


class PeopleFormWidget(HumanResourcesForm):

    FIELDSETS = [
        'h3:PERSONAL INFORMATION',
        (
            segment(
                'full_name',
                ('first_name', 'last_name'),
                ('gender', 'birthday'),
                ('position', 'curriculum_vitae'),
                'biography',
                field_css='fourteen wide',
            ),
            segment(
                '_img',
                '_rotimg_btn',
                'img',
                field_style='max-width:330px;'
            ),
        ),
        'h3:EDUCATION',
        segment('AcademicCareerInline'),
        'h3:CONTACT INFORMATION',
        segment(
            ('email', 'personal_email'),
            ('phone_number', 'phone_extension'),
            'emergency_contact',
            css='secondary'
        ),
        'h3:INSTITUTIONAL INFORMATION',
        segment(
            'InstitutionAffiliationInline',
            ('card_number', 'room'),
            css='secondary'
        ),
    ]

    READ_ONLY = ['full_name', 'auth_user', 'email', 'card_number']

    INLINES = [
        AcademicCareerInline,
        InstitutionAffiliationInline,
    ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def has_permissions(cls, user):
        from .people_list import PeopleListWidget
        return PeopleListWidget.has_permissions(user)

    def has_remove_permissions(self):
        return False

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Member: {0}".format(obj.name)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)
