from pyforms.basewidget import BaseWidget, no_columns
from pyforms.controls   import ControlHtml
from pyforms.controls   import ControlEmail
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlDate
from pyforms.controls   import ControlQueryCombo

from django.core.mail   import EmailMessage
from django.utils import timezone

from django.conf import settings
from confapp import conf

from news.models import MailingList


class PreviewApp(BaseWidget):

    UID = 'communications-previsualisation'
    TITLE = 'Preview communications'

    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'desktop'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._htmlcontrol = ControlHtml('Pre-visualisation')
        self._email       = ControlEmail('Email')
        self._send_btn    = ControlButton(
            '<i class="mail outline icon"></i>Send Newsletter',
            css='fluid primary',
        )
        self._preview_date = ControlDate('Preview date')
        self._preview_btn  = ControlButton(
            '<i class="refresh icon"></i>Preview',
            css='fluid',
        )
        self._mailing_list = ControlQueryCombo('Mailing list', queryset=MailingList.objects.all(), display_column='name')

        self.formset = [
            no_columns('_mailing_list' ,'_preview_date', '_preview_btn','_email','_send_btn', ),
            '_htmlcontrol'
        ]

        self._send_btn.value = self.__sendto_event
        self._preview_btn.value         = self.__preview_event

        self.__preview_event()
        self._email.hide()

    def __sendto_event(self):

        if self._email.visible is False:
            self._email.show()
        elif not self._email.value:
            self.alert('Please specify an email address', 'Error')
        elif self._mailing_list.value:

            lst = MailingList.objects.get(pk=self._mailing_list.value)
            self._htmlcontrol.label = lst.name
            self._htmlcontrol.value = lst.render_template(when=self._preview_date.value)

            try:
                msg = EmailMessage(
                    lst.name,
                    lst.render_template(when=self._preview_date.value),
                    settings.DEFAULT_FROM_EMAIL,
                    (self._email.value,)
                )
                msg.content_subtype = "html"
                msg.send()
                self.success('Email sent with success', 'Success')
                self._email.hide()
            except Exception as e:
                self.alert(str(e), 'Error')

    def __preview_event(self):

        if self._mailing_list.value:
            lst = MailingList.objects.get(pk=self._mailing_list.value)
            self._htmlcontrol.label = lst.name
            self._htmlcontrol.value = lst.render_template(when=self._preview_date.value)
            self._send_btn.enabled = True
        else:
            self._htmlcontrol.value = None
            self._send_btn.enabled = False

