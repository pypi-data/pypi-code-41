from django.contrib.staticfiles.templatetags.staticfiles import static

from django.conf import settings
from confapp import conf
from pyforms_web.web.middleware import PyFormsMiddleware
from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.widgets.django import ModelFormWidget
from pyforms.basewidget import segment
from pyforms.controls import ControlImg
from pyforms.controls import ControlSimpleLabel
from pyforms.controls import ControlEmptyWidget

from people.models import Person
from people.models import GroupMembership

from .people.inline_institution_affiliation import InstitutionAffiliationInline
from .people.inline_academic_career import AcademicCareerInline
from .people.inline_groups import GroupsInline

try:
    from humanresources.models import PrivateInfo
    from humanresources.apps.people.profile_privateinfo import ProfilePrivateInfoFormWidget
    hr_module_installed = 'humanresources' in settings.INSTALLED_APPS
except:
    hr_module_installed = False

class ProfileGroupsInline(GroupsInline):

    def has_add_permissions(self):
        return False

    def has_view_permissions(self, obj):
        return False

    def has_update_permissions(self, obj):
        return False

    def has_remove_permissions(self, obj):
        return False


class UserProfileFormWidget(ModelFormWidget):

    UID = 'profile'
    TITLE = 'My Profile'

    MODEL = Person

    LAYOUT_POSITION = conf.ORQUESTRA_HOME

    ORQUESTRA_MENU = 'top'
    ORQUESTRA_MENU_ICON = 'user'
    ORQUESTRA_MENU_ORDER = 1

    HAS_CANCEL_BTN_ON_EDIT = False

    READ_ONLY = (
        'full_name',
        'gender',
        'img',
        'card_number',
        'phone_extension',
        'position',
    )

    FIELDSETS = [
        segment(
            ('_summary', '_img',),
        ),
        'h3:PERSONAL INFORMATION',
        {
            '1:General': [
                ('gender', 'birthday'),
                ('personal_email', 'phone_number'),
                'curriculum_vitae',
                'emergency_contact',
            ],
            '2:Public': [
                # 'info:The information provided in the fields below will be shared publicly.',
                ('first_name', 'last_name'),
                'biography',
            ],
            '3:Private': ['_privateinfo'] if hr_module_installed else None,
            '4:Institutional': [
                ('card_number', 'phone_extension'),
                'ProfileGroupsInline',
            ],
            '5:Affiliation':[
                'InstitutionAffiliationInline',
            ],
            '6:Education': [
                'AcademicCareerInline',
            ],
        },
    ]

    INLINES = [
        InstitutionAffiliationInline,
        ProfileGroupsInline,
        AcademicCareerInline,
    ]

    def __init__(self, *args, **kwargs):
        user = PyFormsMiddleware.user()
        person = Person.objects.get(auth_user=user)
        super().__init__(pk=person.pk, *args, **kwargs)

        membership = GroupMembership.objects.filter(person=person).first()
        membership_html = (
            f'<h3><a>{membership.group}</a> - {membership.position}</h3>'
            if membership is not None
            else ''
        )
        s = (
            f'<h1>{person.full_name}</h1>'
            '<address>'
            f'{membership_html}'
            '\n'
            f'<a href="mailto:{person.email}" target="_blank">'
            f'<i class="envelope icon"></i>{person.email}</a>'
            '</address>'
        )
        self._summary = ControlSimpleLabel(
            default=s,
            label_visible=False,
            field_css='fourteen wide',
        )

        if hr_module_installed:
            privateinfo, _ = PrivateInfo.objects.get_or_create(person=person)
            self._privateinfo = ControlEmptyWidget(
                parent=self,
                name='_privateinfo',
                default=ProfilePrivateInfoFormWidget(
                    pk=privateinfo.pk,
                    has_cancel_btn=False,
                ),
            )
        
        try:
            img_url = self.model_object.thumbnail_url(geometry_string='300x300')
        except AttributeError:
            img_url = static('square-image.png')
        self._img = ControlImg('Image', default=img_url, label_visible=False,
                               field_css='three wide')

    def save_form_event(self, obj):
        self._privateinfo.value.save_form_event(self._privateinfo.value.model_object)
        super().save_form_event(obj)

    def has_remove_permissions(self):
        return False
