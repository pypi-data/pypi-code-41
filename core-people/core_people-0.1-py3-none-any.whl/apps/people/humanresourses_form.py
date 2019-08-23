from PIL import Image
from sorl.thumbnail import delete

from confapp import conf

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.models import Group as AuthGroup

from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.widgets.django import ModelFormWidget
from pyforms.basewidget import segment
from pyforms.basewidget import no_columns
from pyforms.controls import ControlImg
from pyforms.controls import ControlButton

from people.models import InstitutionAffiliation
from people.models import AcademicCareer
from people.models import Person
from people.models import GroupMembership

from django.conf import settings

try:
    from humanresources.apps.people.privateinfo import PrivateInfoFormWidget
    from humanresources.apps.proposals import ContractProposalsListWidget
    from humanresources.apps.contracts import ContractsListWidget
    hr_module_installed = 'humanresources' in settings.INSTALLED_APPS
except:
    hr_module_installed = False



from .inline_academic_career import AcademicCareerInline
from .inline_auth_groups import AuthGroupsInline
from .inline_groups import GroupsInline
from .inline_institution_affiliation import InstitutionAffiliationInline










class HumanResourcesForm(ModelFormWidget):
    """
    The advanced version of the form should only be available to
    administrators.
    """
    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB

    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE        = True

    FIELDSETS = [
        no_columns('_privateinfo_btn', '_proposals_btn', '_contracts_btn', 'active'),
        ' ',
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
            )
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
            'auth_user',
            css='secondary'
        ),
        'h3:GROUPS',
        segment('GroupsInline', css='blue'),
        'h3:AUTH GROUPS',
        segment('AuthGroupsInline', css='red')
    ]

    READ_ONLY = ['auth_user']

    INLINES = [
        AcademicCareerInline,
        InstitutionAffiliationInline,
        GroupsInline,
        AuthGroupsInline,
    ]

    AUTHORIZED_GROUPS = ['superuser']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self, 'active'):
            self.active.label_visible = False
            self.active.field_style = 'text-align: right;margin-top:5px;'
            self.active.field_css = 'two wide'

        self._rotimg_btn = ControlButton(
            '<i class="icon undo" ></i>Rotate',
            default=self.__rotimg_evt,
            label_visible=False,
            style='margin-top:5px;',
            field_style='text-align: right;',
            css='mini')

        self._img = ControlImg('Image', label_visible=False)

        self.img.changed_event = self.__update_image_evt

        ###############################################
        ## Human Resources related buttons
        ###############################################
        self._privateinfo_btn = ControlButton(
            '<i class="icon lock" ></i>Private info',
            default=self.__privateinfo_btn_evt,
            label_visible=False,
            css='basic red'
        )
        self._contracts_btn = ControlButton(
            '<i class="icon file alternate" ></i>Contracts',
            default=self.__contracts_btn_evt,
            label_visible=False,
            css='basic'
        )
        self._proposals_btn = ControlButton(
            '<i class="icon file alternate outline" ></i>Proposals',
            default=self.__proposals_btn_evt,
            label_visible=False,
            css='basic'
        )

        # Only show this buttons if the humanresources modules is installed.
        if not hr_module_installed:
            self._privateinfo_btn.hide()
            self._contracts_btn.hide()
            self._proposals_btn.hide()
        else:
            if self.model_object is None:
                self._contracts_btn.hide()
                self._proposals_btn.hide()
                self._privateinfo_btn.hide()

        if self.model_object is not None:
            self.__update_image_evt()

    @classmethod
    def has_permissions(cls, user):
        from .humanresources_list import HumanResourcesList
        return HumanResourcesList.has_permissions(user)

    def __update_image_evt(self):
        url = self.model_object.thumbnail_url(geometry_string='300x300')
        self._img.value = url + '?t=' + str(timezone.now().timestamp())

    def __rotimg_evt(self):
        delete(self.img.filepath, delete_file=False)
        im = Image.open(self.img.filepath)
        rot = im.rotate(90)
        rot.save(self.img.filepath)
        self.__update_image_evt()

    def __privateinfo_btn_evt(self):
        obj = self.model_object
        if obj:
            privateinfo = obj.get_privateinfo()
            app = PrivateInfoFormWidget(
                pk=privateinfo.pk,
                title=str(privateinfo),
                has_cancel_btn=False,
            )
            app.LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB

    def __proposals_btn_evt(self):
        obj = self.model_object
        if not obj:
            return

        app = ContractProposalsListWidget(
            parent_pk=obj.pk,
            parent_model=Person,
            has_cancel_btn=False,
        )
        app.LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB

    def __contracts_btn_evt(self):
        obj = self.model_object
        if not obj:
            return

        app = ContractsListWidget(
            parent_pk=obj.pk,
            parent_model=Person,
            has_cancel_btn=False,
        )
        app.LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Person: {0}".format(obj.name)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)