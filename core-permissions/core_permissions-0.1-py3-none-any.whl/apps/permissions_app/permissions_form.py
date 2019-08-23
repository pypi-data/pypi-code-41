from django.apps import apps
from django.contrib.auth.models import Group as AuthGroup, User, Permission
from django.contrib.contenttypes.models import ContentType

from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.basewidget import no_columns
from pyforms.basewidget import segment
from pyforms.controls import ControlButton
from pyforms.controls import ControlList
from pyforms.controls import ControlText
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlAutoComplete
from pyforms_web.widgets.django import ModelFormWidget

from people.models import Group as ResearchGroup


def chunks(l, n):
    n = max(1, n)
    return [
        tuple(l[i:i+n] + [' '] * (n-len(l[i:i+n])))
        for i in range(0, len(l), n)
    ]


class GroupMembersWidget(BaseWidget):

    LAYOUT_POSITION = conf.LAYOUT_NEW_WINDOW

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        super().__init__(self, *args, **kwargs)

        if isinstance(self.group, AuthGroup):
            users = self.group.user_set.all()
            users = users.values_list('username', flat=True)
        elif isinstance(self.group, ResearchGroup):
            people = self.group.members.all()
            users = [person.auth_user.username for person in people]
        else:
            raise ValueError('Invalid group type')

        users = [(u, ) for u in users]

        self._list = ControlList(
            horizontal_headers=['username'],
            default=list(users),
        )

        self.title = str(self.group)
        self.formset = ['_list' if users else ' ']


class EditGroupWindow(BaseWidget):

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_WINDOW

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._group = kwargs.get('group', None)

        self._groupname = ControlText('Name', default=self._group.name if self._group else None)
        self._savebtn = ControlButton('Save', default=self.__save_btn_evt, label_visible=False)

        self.formset = ['_groupname', '_savebtn']

    def __save_btn_evt(self):
        if self._groupname.value.strip():
            if self._group:
                obj = AuthGroup.objects.get(pk=self._group.pk)
            else:
                obj = AuthGroup()

            obj.name = self._groupname.value
            obj.save()
            self.close()


class PermissionsFormWidget(ModelFormWidget):

    MODELS_TO_MANAGE = (
        'humanresources.contract',
        'humanresources.contractproposal',
        'people.person',
        'research.publication',

        # 'finance.budget',
        # 'finance.financecostcenter',
        # 'finance.financeproject',
        'orders.order',
    )

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE = True

    AUTHORIZED_GROUPS = ['superuser']

    READ_ONLY = (
        'auth_user',
    )

    FIELDSETS = [
        ('ranking', ' '),
        no_columns('djangogroup', '_editgrpbtn', '_newgrpbtn', ' ', 'researchgroup', '_users_in_research_group_detail_btn'),
        '_members',
    ]

    def __init__(self, *args, **kwargs):

        self._members = ControlAutoComplete(
            'Members',
            queryset=User.objects.all().order_by('username'),
            multiple=True,
            queryset_filter=self.__members_queryset_filter
        )

        super().__init__(self, *args, **kwargs)

        self._newgrpbtn = ControlButton(
            label='<i class="plus icon"></i>',
            helptext='Add new group',
            default=self.__new_profile_btn_evt,
            css='blue circular ui icon button',
        )
        self._editgrpbtn = ControlButton(
            label='<i class="edit icon"></i>',
            helptext='Edit selected group',
            default=self.__edit_profile_btn_evt,
            css='basic circular ui icon button',
        )

        self._users_in_research_group_detail_btn = ControlButton(
            label='<i class="fitted eye icon"></i>',
            helptext='View group members',
            default=self.__list_research_group_users,
            css='circular ui icon button',
            field_css='two wide',
        )

        self._members = ControlAutoComplete(
            'Members',
            queryset=User.objects.all().order_by('username'),
            multiple=True,
            queryset_filter=self.__members_queryset_filter
        )

        self.djangogroup.field_css = 'fourteen wide'
        self.researchgroup.field_css = 'fourteen wide'

        self.djangogroup.update_control_event = self.__group_selection_changed
        self.researchgroup.update_control_event = self.__group_selection_changed

        # Create the permissions controls
        for perm in self.__permissions_to_manage():
            control = ControlCheckBox(perm.name, label_visible=False)
            setattr(self, perm.codename, control)

        self.__group_selection_changed()
        self.__populate_members()
        self.__populate_permissions()

    def __permissions_to_manage(self):
        """
        Generator for all permissions to be listed in the app form.
        Returns default model permissions first, followed by custom
        permissions if they exist.

        Select the desired models using `MODELS_TO_MANAGE`.
        """

        for model_name in self.MODELS_TO_MANAGE:
            try:
                model = apps.get_model(model_name)
            except LookupError:
                continue

            content_type = ContentType.objects.get_for_model(model)

            permissions = Permission.objects.filter(content_type=content_type)

            # retrieve default permissions first
            default_codenames = list(map(
                lambda x: f'{x}_{content_type.model}',
                ('view', 'add', 'change', 'delete'),
            ))
            for default_codename in default_codenames:
                perm = permissions.get(codename=default_codename)
                yield perm

            # and finally any custom defined permissions
            for custom_perm in permissions\
                    .exclude(codename__in=default_codenames)\
                    .order_by('name'):
                    yield custom_perm

    def __populate_permissions(self):
        """
        Configure the permissions checkboxes for the selected django group
        """
        if self.djangogroup.value:
            grpid = self.djangogroup.value
            grp = AuthGroup.objects.get(pk=grpid)
            for perm in Permission.objects.all():
                if hasattr(self, perm.codename):
                    if grp.permissions.filter(pk=perm.pk).exists():
                        getattr(self, perm.codename).value = True
                    else:
                        getattr(self, perm.codename).value = False

    def get_fieldsets(self, default):
        """
        Build the field organization
        """
        default = default + ['-']

        last = None
        fields = []
        for perm in self.__permissions_to_manage():
            if last != perm.content_type:
                if fields:
                    default = default + ['h3:'+last.model_class()._meta.verbose_name_plural, segment(chunks(fields, 4))]
                last = perm.content_type
                fields = []

            fields = fields + [perm.codename]

        default = default + ['h3:'+last.model_class()._meta.verbose_name_plural, segment(chunks(fields, 4))]
        return default

    def save_object(self, obj, **kwargs):
        obj = super().save_object(obj, **kwargs)

        # Save the group users
        users = User.objects.filter(pk__in=self._members.value)
        obj.djangogroup.user_set.set(users)

        # Save the permissions to the group
        permissions = []
        for perm in self.__permissions_to_manage():
            field = getattr(self, perm.codename)
            if field.value:
                permissions.append(perm)
        obj.djangogroup.permissions.set(permissions)

        return obj

    def __new_profile_btn_evt(self):
        EditGroupWindow(title='Create a new profile')

    def __edit_profile_btn_evt(self):
        if self.djangogroup.value:
            obj = AuthGroup.objects.get(pk=self.djangogroup.value)
            EditGroupWindow(title='Rename Profile', group=obj)
            # TODO update value in combobox

    def __members_queryset_filter(self, qs, keyword, control):
        if keyword:
            qs = qs.filter(username__icontains=keyword)

        return qs

    def __permissions_queryset_filter(self, qs, keyword, control):
        qs = qs.filter()

        if keyword:
            qs = qs.filter(name__icontains=keyword)

        return qs

    def __populate_members(self):
        if self.djangogroup.value:
            grp = AuthGroup.objects.get(pk=self.djangogroup.value)
            self._members.value = [obj.pk for obj in grp.user_set.all()]
        else:
            self._members.value = []

    def __group_selection_changed(self):
        """Disabled the button if the group is empty."""
        self._users_in_research_group_detail_btn.enabled = bool(self.researchgroup.value)
        self.__populate_members()
        self.__populate_permissions()

    def __list_research_group_users(self):
        group = ResearchGroup.objects.get(pk=self.researchgroup.value)
        GroupMembersWidget(group=group)

    def autocomplete_search(self, queryset, keyword, control):
        qs = super().autocomplete_search(queryset, keyword, control)

        if control.name == 'djangogroup' and keyword is not None:
            return qs.filter(name__icontains=keyword)
        else:
            return qs

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Permissions: {0}-{1}".format(obj.djangogroup, obj.researchgroup)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)
