from confapp import conf
from django.conf import settings
from people.models import Person
from pyforms.basewidget import segment
from pyforms.controls import ControlImg
from .memberships import MembershipsListWidget
from pyforms_web.widgets.django import ModelFormWidget

try:
    from research.apps.groups.projects import ProjectsListWidget
    research_module_installed = 'research' in settings.INSTALLED_APPS
except:
    research_module_installed = False

class GroupFormApp(ModelFormWidget):

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE = True
    TITLE = 'Group'



    INLINES = [MembershipsListWidget] + ([ProjectsListWidget] if research_module_installed else [])

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB

    FIELDSETS = [
        ('type', 'responsible'),
        ' ',
        (
            segment(
                'h3: IDENTIFICATION',
                'name',
                'subject',
                field_css='fourteen wide',
            ),
            segment(
                '_img',
                field_style='max-width:330px;'
            )
        ),
        {
            '1:Group Information': [
                'description', 'web', 'logo_img', '_grpimg',
            ],
            '2:Members': ['MembershipsListWidget'],
            '3:Projects': ['ProjectsListWidget'] if research_module_installed else None,
        }
    ]

    def __init__(self, *args, **kwargs):

        self._img = ControlImg('Image', label_visible=False)
        self._grpimg = ControlImg('Image', label_visible=False)

        super().__init__(*args, **kwargs)

        self.responsible.changed_event = self.__update_image_evt

        self.logo_img.changed_event = self.__update_group_img_evt

        self.__update_image_evt()
        self.__update_group_img_evt()

    def __update_group_img_evt(self):
        self._grpimg.value = self.logo_img.value

    def __update_image_evt(self):
        try:
            person = Person.objects.get(pk=self.responsible.value.pk)
            url = person.thumbnail_url('300x300')
        except:
            url = Person.DEFAULT_PICTURE_URL

        self._img.value = url

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Group: {0}".format(obj.name)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)
