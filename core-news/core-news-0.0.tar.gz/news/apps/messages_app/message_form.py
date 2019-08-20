from confapp import conf
from pyforms.basewidget import no_columns, segment
from pyforms_web.widgets.django import ModelFormWidget

from news.models import Message

class MessageForm(ModelFormWidget):

    TITLE = 'Message'
    MODEL = Message

    FIELDSETS = [
        ('mailing_lists', 'publish_start', 'publish_end', 'order'),
        'subject',
        ' ',
        segment(
            'name',
            'image',
            'text',
            css='red'
        ),
        ('is_event', 'date', 'location', 'start', 'end'),
        ' '
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_event.changed_event = self.__is_event_changed_evt

        self.__is_event_changed_evt()

    def __is_event_changed_evt(self):
        if self.is_event.value:
            self.date.hide()
            self.location.show()
            self.start.show()
            self.end.show()
        else:
            self.date.show()
            self.location.hide()
            self.start.hide()
            self.end.hide()