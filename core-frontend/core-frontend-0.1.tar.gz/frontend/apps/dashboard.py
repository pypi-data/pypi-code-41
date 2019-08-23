from pyforms_web.basewidget import BaseWidget
from confapp import conf

from pyforms_web.controls.control_button import ControlButton
from pyforms_web.controls.control_text import ControlText
from pyforms_web.controls.control_list import ControlList

from pyforms.basewidget import segment
from pyforms.basewidget import no_columns

class DashboardWidget(BaseWidget):
    """
    """
    UID = 'dashboard'
    TITLE = 'Dashboard'

    LAYOUT_POSITION = conf.ORQUESTRA_HOME

    ORQUESTRA_MENU = 'left'
    ORQUESTRA_MENU_ICON = 'desktop'
    ORQUESTRA_MENU_ORDER = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._people    = ControlButton(
            '<i class="icon users"></i>People', css=' circular ', label_visible=False,
            default='window.location="/app/people/";')
        self._contracts = ControlButton(
            '<i class="icon file outline"></i>Contracts', css=' circular ', label_visible=False,
            default='window.location="/app/contracts/";')
        self._proposals = ControlButton(
            '<i class="icon file"></i>Proposals', css=' circular ', label_visible=False,
            default='window.location="/app/proposals/";')

        self._orders = ControlButton(
            '<i class="icon dollar"></i>Orders', css=' circular ', label_visible=False,
            default='window.location="/app/orders/";')

        self.formset = [
            'h2:Human resources',
            no_columns('_people','_contracts','_proposals'),
            '-',
            'h2:Orders',
            no_columns('_orders')
        ]