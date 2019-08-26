from django.conf import settings

from confapp import conf
from pyforms.basewidget import segment
from pyforms.basewidget import no_columns
from pyforms.controls import ControlButton
from pyforms_web.widgets.django import ModelFormWidget
from pyforms_web.web.middleware import PyFormsMiddleware

from orders.models import Order

from .orderexpensecode_list import OrderExpenseCodeInline
from .orderfile_list import OrderFileInline


class OrderEditFormWidget(ModelFormWidget):

    MODEL = Order
    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    HAS_CANCEL_BTN_ON_EDIT = False

    CLOSE_ON_REMOVE = True

    TITLE = 'Edit order'

    READ_ONLY = ['responsible', ]

    INLINES = [OrderExpenseCodeInline, OrderFileInline]

    FIELDSETS = [
        ('order_req', 'group'),
        (
            segment(
                'finance',
                'order_desc',
                ('order_amount', 'currency', 'order_paymethod'),
                field_css='fourteen wide',
            ),
            segment(
                ('order_reqnum', 'order_reqdate'),
                ('order_podate', 'expected_date'),
                ('order_deldate', ' '),
                'order_notes',
                css='secondary',
            ),
        ),
        segment(
            'OrderExpenseCodeInline',
            css='green'
        ),
        segment(
            'OrderFileInline',
            css='blue'
        ),
        no_columns('responsible',)
    ]

    AUTHORIZED_GROUPS = ['superuser', settings.APP_PROFILE_ORDERS]

    @classmethod
    def has_permissions(cls, user):
        from .orders_list import OrderAdminWidget
        return OrderAdminWidget.has_permissions(user)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = PyFormsMiddleware.user()

        # Filter Auth Groups to the groups the user is a member of.
        self.group.queryset = self.group.queryset.order_by('name')
        if not user.is_superuser:
            self.group.queryset = self.group.queryset & user.groups.all()

        if self.group.queryset.count() == 1:
            self.group.value = self.group.queryset.first().pk

        if self.object_pk is not None:
            self._duplicate_btn = ControlButton(
                'Duplicate',
                default=self.__duplicate_btn_evt,
                label_visible=False,
                css='basic brown'
            )

    def autocomplete_search(self, queryset, keyword, control):
        qs = super().autocomplete_search(queryset, keyword, control)

        if control.name=='group' and keyword is not None:
            return qs.filter(name__icontains=keyword)
        else:
            return qs

    def __duplicate_btn_evt(self):
        user = PyFormsMiddleware.user()
        order = self.model_object.duplicate(user)
        OrderEditFormWidget(pk=order.pk, parent_win=self.parent)

    def get_buttons_row(self):
        buttons = []
        if self.has_update_permissions():   buttons.append('_save_btn')
        if self.has_add_permissions():      buttons.append('_create_btn')
        if self.has_cancel_btn:             buttons.append('_cancel_btn')
        if self.has_remove_permissions():   buttons.append('_remove_btn')
        if self.object_pk is not None:      buttons.append('_duplicate_btn')
        return [no_columns(*buttons)]

    def create_newobject(self):
        obj = super().create_newobject()
        obj.responsible = PyFormsMiddleware.user()
        return obj

    def delete_event(self):
        res = super().delete_event()
        self._duplicate_btn.hide()
        return res

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Order: {0}".format(obj.order_id)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)
