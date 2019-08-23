import os
from pyforms.basewidget import BaseWidget, segment
from pyforms.controls import ControlLabel
from pyforms.controls import ControlButton
from pyforms.controls import ControlList
from pyforms.controls import ControlText
from pyforms.controls import ControlAutoComplete
from pyforms.controls import ControlEmptyWidget
from confapp import conf
from django.conf import settings
from .search_publications import PubsList
from people.models import Person
from research.models import AuthorAlias


class UpdatePublication(BaseWidget):

    TITLE = 'Search publication'

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_BIGWINDOW

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        authors      = kwargs.get('authors')
        title        = kwargs.get('title')
        journal_name = kwargs.get('journal_name')
        doi          = kwargs.get('doi')
        pubdate      = kwargs.get('pubdate')
        pubyear      = kwargs.get('pubyear')

        self.pub_hash = str( (authors, title, journal_name, doi, pubdate, pubyear) )

        text = f"""
            <table>
                <tr>
                    <th style='text-align: right' >Title</th>
                    <td style='padding:5px;padding-left:10px;' colspan='3' >{title}</th>
                <tr/>
                <tr>
                    <th style='text-align: right' >Authors</th>
                    <td style='padding:5px;padding-left:10px;' colspan='3' >{authors}</th>
                <tr/>
                <tr>
                    <th style='text-align: right' >Journal</th>
                    <td style='padding:5px;padding-left:10px;' >{journal_name}</th>
                    <th style='text-align: right' >Pub date</th>
                    <td style='padding:5px;padding-left:10px;' >{pubdate}</th>
                <tr/>
                <tr>
                    <th style='text-align: right' >Year</th>
                    <td style='padding:5px;padding-left:10px;' >{pubyear}</th>
                    <th style='text-align: right' >Doi</th>
                    <td style='padding:5px;padding-left:10px;' >{doi}</th>
                <tr/>
            </table>
        """

        self._person = ControlAutoComplete(
            'Author',
            queryset=Person.objects.all().order_by('full_name'),
            visible=False
        )
        self._authoralias = ControlText(
            'Author alias',
            visible=False
        )
        self._addalias = ControlButton(
            'Add alias',
            default=self.__add_author_alias_evt,
            visible=False
        )

        alias = AuthorAlias.objects.all()

        self._authors   = ControlList(
            'Unknown authors',
            default=[[a] for a in authors.split(';') if not alias.filter(name=a).exists()],
            horizontal_headers=['Authors alias'],
            item_selection_changed_event=self.__authors_selection_changed_evt
        )

        self._ignorebtn = ControlButton(
            'Ignore this publication', css='red', default=self.__ignore_this_pub_evt,
            label_visible=False
        )
        self._info    = ControlLabel(text)
        self._details = ControlEmptyWidget(parent=self, name='_details', default=PubsList(**kwargs))

        self.formset = [
            '_ignorebtn',
            '_info',
            ('_person', '_authoralias', '_addalias'),
            '_authors',
            segment('_details', css='secondary')
        ]

        if len(self._authors.value)==0:
            self._authors.hide()


    def __authors_selection_changed_evt(self):
        if self._authors.selected_row_index>=0:
            self._addalias.show()
            self._authoralias.show()
            self._person.show()
            self._authoralias.value = self._authors.value[self._authors.selected_row_index][0]
        else:
            self._addalias.hide()
            self._authoralias.hide()
            self._person.hide()

    def __add_author_alias_evt(self):

        if self._authoralias.value and self._person.value:
            a = AuthorAlias(
                name=self._authoralias.value,
                person=Person.objects.get(pk=self._person.value)
            )
            a.save()

            data = self._authors.value
            newdata = []
            for row in data:
                if row[0]==self._authoralias.value: continue
                newdata.append(row)
            self._authors.value = newdata

            self._addalias.hide()
            self._authoralias.hide()
            self._person.hide()

    def __ignore_this_pub_evt(self):

        filepath = os.path.join(
            settings.MEDIA_ROOT,
            conf.APP_IMPORT_PUBLICATIONS_BLACKLIST_FILE
        )

        with open(filepath, 'a') as out:
            out.write(str(self.pub_hash)+'\n')

        self.close()

    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser:
            return True

        return user.groups.filter(
            permissions__codename__in=['app_access_imp_pub']
        ).exists()