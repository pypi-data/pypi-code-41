from django.conf import settings

from confapp import conf
from pyforms.basewidget import segment
from pyforms_web.web.middleware import PyFormsMiddleware
from pyforms_web.widgets.django import ModelAdminWidget

from finance.models import ExpenseCode


class ExpenseCodeListApp(ModelAdminWidget):

    TITLE = 'Expense codes'

    MODEL = ExpenseCode

    LIST_DISPLAY = ['number', 'type']

    FIELDSETS = [
        segment(
            # 'financeproject',  # not required if app used as Inline
            ('number', 'type')
        )
    ]

    # ORQUESTRA CONFIGURATION
    # =========================================================================
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    # =========================================================================

    AUTHORIZED_GROUPS = ['superuser', settings.PROFILE_LAB_ADMIN]

    def has_add_permissions(self):
        finance_project = self.parent_model.objects.get(pk=self.parent_pk)
        if finance_project.financeproject_code == 'NO TRACK':
            return False
        else:
            return True

    def has_update_permissions(self, obj):
        if obj and obj.financeproject.financeproject_code == 'NO TRACK':
            return False
        else:
            return True

    def has_remove_permissions(self, obj):
        """Only superusers may delete these objects."""
        user = PyFormsMiddleware.user()
        return user.is_superuser
