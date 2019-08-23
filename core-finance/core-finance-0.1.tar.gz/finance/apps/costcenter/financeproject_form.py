from confapp import conf
from pyforms.basewidget import segment
from pyforms_web.widgets.django import ModelFormWidget

from finance.models import Project

from .expensecode_list import ExpenseCodeListApp


class FinanceProjectFormApp(ModelFormWidget):

    TITLE = 'Finance project'

    MODEL = Project

    INLINES = [ExpenseCodeListApp]

    FIELDSETS = [
        ('grant', 'currency'),
        segment(
            ('name', 'code', 'responsible'),
            ('start_date', 'end_date', ' '),
            ('total_amount', 'importoverheads', 'funding'),
        ),
        ' ',
        'ExpenseCodeListApp',
        ' ',
    ]

    # ORQUESTRA CONFIGURATION
    # =========================================================================
    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    # =========================================================================

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Proj: {0}".format(obj.name)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)
