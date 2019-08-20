from django.conf import settings

from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlInteger
from pyforms.controls import ControlButton
from pyforms.controls import ControlLineChart
from pyforms.controls import ControlPieChart
from pyforms.controls import ControlList
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlAutoComplete

from django.db.models import Count
from research.models  import Publication, PubType

from pyforms_web.organizers import segment, no_columns
from confapp import conf

class PublicationsReports(BaseWidget):

    UID   = 'publications-report'
    TITLE = 'Report'

    LAYOUT_POSITION = conf.ORQUESTRA_HOME_FULL
    ORQUESTRA_MENU = 'left>PublicationsListWidget'
    ORQUESTRA_MENU_ORDER = 20
    ORQUESTRA_MENU_ICON = 'chart line'

    AUTHORIZED_GROUPS = [
        'superuser',
        settings.PROFILE_SCICOM,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._startyear = ControlInteger('Start year')
        self._endyear   = ControlInteger('End year')
        self._keypubs   = ControlCheckBox('Pub. types', default=False)
        self._pubtypes  = ControlAutoComplete('Publications types', multiple=True, queryset=PubType.objects.all())
        self._applybtn  = ControlButton('Apply', default=self.populate_graph)

        self._linegraph     = ControlLineChart('Publications per year')
        #self._journalschart = ControlPieChart('Publications per journal')
        self._journalslist  = ControlList('Publications per journal', horizontal_headers=['Journals', 'N pubs', '%'])

        self.formset = [
            no_columns('_startyear', '_endyear', '_pubtypes', '_keypubs', '_applybtn'),
            segment('_linegraph'),
            '_journalslist'
        ]

    def get_pubs_queryset(self):
        start = self._startyear.value
        end   = self._endyear.value
    
        qs = Publication.objects.all()

        if start: qs = qs.filter(publication_year__gte=start)
        if end:   qs = qs.filter(publication_year__lte=end)
        if self._keypubs.value:
            qs = qs.key_publications()

        if self._pubtypes.value:
            qs = qs.filter(pubtype__in=self._pubtypes.value)

        return qs

    def populate_graph(self):
        
        
        qs = self.get_pubs_queryset()
        qs = qs.values('publication_year').annotate(total=Count('publication_year')).order_by('publication_year')

        rows = [(int(row['publication_year']), row['total']) for row in qs]

        self._linegraph.value = {'Publications': rows}

        

        qs = self.get_pubs_queryset()
        
        total = qs.count()

        qs = qs.values('journal__journal_name').annotate(total=Count('journal__journal_name')).order_by('journal__journal_name')

        rows = [ (row['journal__journal_name'], row['total'], round((row['total']/total)*100,2) ) for row in qs]
        rows = sorted(rows, key=lambda x: -x[1])
        
        #self._journalschart.value = rows
        self._journalslist.value  = rows