from django.db.models import Q
from pyforms.controls import ControlFileUpload
from pyforms.controls import ControlList
from pyforms.controls import ControlButton
from pyforms.basewidget import BaseWidget, no_columns
from confapp import conf
import csv, os
from dateutil.parser import parse as parse_date
from research.models import Publication, Journal
from .update_journal import UpdateJournal
from .update_publications.update_publication import UpdatePublication
from django.conf import settings


class ImportPublications(BaseWidget):

    UID = 'import-publications'
    TITLE = 'Import publications'

    LAYOUT_POSITION = conf.ORQUESTRA_HOME_FULL
    ORQUESTRA_MENU = 'left>PublicationsListWidget'
    ORQUESTRA_MENU_ORDER = 30
    ORQUESTRA_MENU_ICON = 'cloud upload teal'



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._file   = ControlFileUpload('Web of science file', field_css='seven wide')
        self._import = ControlButton('Import', default=self.__import_evt)
        self._clear  = ControlButton('Clear blacklist', default=self.__clear_cache_evt, css='basic red')
        self._list   = ControlList('Pubs',
            horizontal_headers=[
                'Errors',
                'Authors',
                'Title',
                'Journal',
                'DOI',
                'Pub. date',
                'Year'
            ],
            item_selection_changed_event=self.__item_selection_changed_evt
        )

        self.formset = [
            no_columns('_file', '_import', '_clear'),
            '_list',
        ]


    def __clear_cache_evt(self):
        cachefile = os.path.join(
            settings.MEDIA_ROOT,
            conf.APP_IMPORT_PUBLICATIONS_BLACKLIST_FILE
        )
        os.remove(cachefile)
        self.message('The blacklist was reseted.')

    def __fixjournal_evt(self):
        rows = self._list.value
        row  = rows[self._list.selected_row_index]
        journal_name = row[3]
        UpdateJournal(name=journal_name)

    def __item_selection_changed_evt(self):
        rows = self._list.value
        row  = rows[self._list.selected_row_index]

        authors      = row[1]
        title        = row[2]
        journal_name = row[3]
        doi          = row[4]
        pubdate      = row[5]
        pubyear      = row[6]

        journals = Journal.objects.filter(
            Q(journal_name=journal_name) | Q(journalalias__name=journal_name)
        )

        pubs     = Publication.objects.filter(
            Q(publication_title=title) | Q(publication_doi=doi)
        )

        if not journals.exists():
            UpdateJournal(name=journal_name)
        else:
            UpdatePublication(
                authors=authors,
                title=title,
                journal_name=journal_name,
                pubdate=pubdate,
                pubyear=pubyear,
                doi=doi
            )



    def __import_evt(self):
        cachefile = os.path.join(
            settings.MEDIA_ROOT,
            conf.APP_IMPORT_PUBLICATIONS_BLACKLIST_FILE
        )

        cache = []
        if os.path.exists(cachefile):
            with open(cachefile, 'r') as infile:
                for line in infile:
                    cache.append(line[:-1])
        cache = set(cache)

        if not self._file.value: return
        filepath = self._file.filepath
        #filepath = '/home/ricardo/bitbucket/core-project/core-v2/media/apps/import-publications/savedrecs_3g67RpA.csv'

        with open(filepath, encoding='utf-8') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='\t', quotechar='"', )
            heads = next(spamreader)

            authors_col = heads.index('AU')
            title_col = heads.index('TI')
            journal_col = heads.index('SO')
            doi_col = heads.index('DI')
            pubdate_col = heads.index('PD')
            pubyear_col = heads.index('PY')

            rows = []
            for row in spamreader:
                authors      = row[authors_col]
                title        = row[title_col]
                journal_name = row[journal_col]
                doi          = row[doi_col]
                pubdate      = row[pubdate_col]
                pubyear      = row[pubyear_col]

                pub_hash = str((authors, title, journal_name, doi, pubdate, pubyear))

                if pub_hash in cache: continue

                journals = Journal.objects.filter(
                    Q(journal_name=journal_name) | Q(journalalias__name=journal_name)
                )
                pubs     = Publication.objects.filter(
                    Q(publication_title=title) | Q(publication_doi=doi)
                )

                if not journals.exists():
                    error = '<i class="ui icon newspaper red"></i>'

                elif pubs.count()>1:
                    error = '<i class="ui icon file outline red">Found {}</i>'.format(pubs.count())

                elif pubs.exists():
                    pub = pubs[0]
                    try:
                        pdate = parse_date(pubdate)
                    except:
                        pdate = None

                    if pub.publication_title!=title:
                        error = '<i class="ui icon file outline red">Name is different</i>'

                    elif pub.publication_doi != doi:
                        error = '<i class="ui icon file outline red">DOI is different</i>'

                    elif pub.publication_authors != authors:
                        error = '<i class="ui icon file outline red">Authors are different</i>'

                    elif int(pub.publication_year) != int(pubyear):
                        error = '<i class="ui icon file outline red">Year is different</i>'

                    elif pdate is not None and (pub.publication_publish.year != pdate.year or pub.publication_publish.month != pdate.month):
                        error = '<i class="ui icon file outline red">Publish date is different</i>'
                    else:
                        error = None

                elif not pubs.exists():
                    error = '<i class="ui icon file outline red"></i>'


                if error is not None:
                    rows.append([error, authors, title, journal_name, doi, pubdate, pubyear])

            self._list.value = rows



    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser:
            return True

        return user.groups.filter(
            permissions__codename__in=['app_access_imp_pub']
        ).exists()