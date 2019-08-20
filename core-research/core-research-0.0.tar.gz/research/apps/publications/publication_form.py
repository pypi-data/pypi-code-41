from pyforms_web.widgets.django import ModelFormWidget
from pyforms_web.organizers import no_columns
from pyforms.controls import ControlButton
from confapp import conf

from ..journals.journal_form import JournalFormWidget

class PublicationFormWidget(ModelFormWidget):

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB

    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE = True

    FIELDSETS = [
        no_columns('publication_keypub', 'publication_active'),
        ' ',
        {
            '1:Required Fields':
                [
                    ('pubtype', 'publication_year', 'journal','_addjounalbtn'),

                    'publication_title',


                    'publication_authors',
                    'authors',
                ],
            '2:Optional Fields':
                [
                    (
                        'publication_doi',
                        'publication_pmid',
                        'publication_web',
                    ),
                    (
                        'publication_received',
                        'publication_accepted',
                        'publication_publish',
                        'publication_volume',
                        'publication_issue',
                        'publication_pages',
                    ),
                ],
            '3:Abstract':
                [
                    'publication_abstract',
                ],
            '4:Book Information':
                [
                    'publication_book',
                    ('publication_company', 'publication_editors'),
                ],
            '5:Attachments':
                [
                    'publication_file',
                ],
        },
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._addjounalbtn = ControlButton('<i class="ui icon newspaper outline"></i>Add journal', default=self.__add_journal_btn_evt)

    def __add_journal_btn_evt(self):
        JournalFormWidget()


    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Publication: {0}".format(obj.publication_title)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)