
from django.conf import settings
from django.core.exceptions import ValidationError

from confapp import conf

from pyforms.controls import ControlButton
from pyforms_web.organizers import no_columns
from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.widgets.django import ModelFormWidget

from finance.models import Budget
from finance.models import BudgetDoc


class ImportBudgetFormWidget(ModelFormWidget):
    TITLE = 'Import Budget'

    MODEL = BudgetDoc

    CREATE_BTN_LABEL = '<i class="upload icon"></i>Import'
    HAS_CANCEL_BTN_ON_ADD = False

    FIELDSETS = ['document', 'year']

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_WINDOW

    AUTHORIZED_GROUPS = ['superuser', settings.PROFILE_EDIT_BUDGET]

    def save_form_event(self, obj, **kwargs):
        obj = self.update_object_fields(obj)

        # Custom validation
        #   need to run the validators individually or else Django
        #   concatenates all erros together
        try:
            obj.clean_fields()
            obj.clean()
            obj.validate_unique()

        except ValidationError as e:
            errors = []  # a list of messages to display using Pyforms alert()

            for error_message in e:
                if isinstance(error_message, tuple):
                    field_name, messages = error_message

                    pyforms_field = getattr(self, field_name)
                    pyforms_field.error = True

                    if len(messages) == 1:
                        field_messages = f'{messages[0]}'
                    else:
                        field_messages = ''
                        for message in messages:
                            field_messages += f'<li>{message}</li>'
                        field_messages = f'<ul>{field_messages}</ul>'

                    html = f'<b>{pyforms_field.label}:</b> {field_messages}'

                else:
                    html = f'{error_message}'

                errors.append(html)

            self.alert(errors)

        else:
            obj.save(**kwargs)
            self.parent.success("Budgets updated successfully!")
            self.close()


class BudgetFormAdmin(ModelFormWidget):

    MODEL = Budget
    TITLE = 'Suppliers'

    FIELDSETS = [
        'expensecode',
        no_columns('year', 'amount'),
    ]

    AUTHORIZED_GROUPS = ['superuser']


class BudgetAdminWidget(ModelAdminWidget):

    UID = 'budgets'
    MODEL = Budget

    TITLE = 'Budgets'

    LIST_DISPLAY = [
        'year',
        'amount',
        'expensecode',
    ]

    LIST_FILTER = [
        'budget_year',
        'expensecode__project',
        'expensecode__number',
        'expensecode__project__costcenter',
    ]

    EDITFORM_CLASS = BudgetFormAdmin

    ###########################################################################
    # ORQUESTRA CONFIGURATION

    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU = 'left>FinancesDashboardWidget'
    ORQUESTRA_MENU_ORDER = 0
    # ORQUESTRA_MENU_ICON = 'dollar'
    AUTHORIZED_GROUPS = ['superuser', settings.PROFILE_EDIT_BUDGET]
    ###########################################################################

    def __init__(self, *args, **kwargs):

        self._import_btn = ControlButton(
            '<i class="upload icon"></i>Import',
            default=self.__import_evt,
            label_visible=False,
            css='basic blue',
            helptext='Import budget list from XLS file',
        )

        super().__init__(*args, **kwargs)

    def get_toolbar_buttons(self, *args, **kwargs):
        add_btn = super().get_toolbar_buttons(*args, **kwargs)
        return no_columns(add_btn, '_import_btn')

    def __import_evt(self):
        ImportBudgetFormWidget(parent_win=self)
