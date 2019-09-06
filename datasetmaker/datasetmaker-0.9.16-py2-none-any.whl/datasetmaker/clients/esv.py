import io
import zipfile
import pandas as pd
import requests
from frame2package import Frame2Package
from datasetmaker.models import Client


class ESVClient(Client):
    url = ('https://www.esv.se/psidata/arsutfall/GetFile/?documentType=Utgift'
           '&fileType=Zip&fileName=%C3%85rsutfall%20utgifter%202006%20-%202018'
           ',%20definitivt.zip&year=2018&month=0&status=Definitiv')

    def _fetch_archive(self):
        r = requests.get(self.url)
        zipdata = io.BytesIO()
        zipdata.write(r.content)
        z = zipfile.ZipFile(zipdata)
        z.extractall()
        csv = z.filelist[0]
        string = z.read(csv).decode('utf8')
        return string

    def get(self, indicators=None, periods=None):
        data_string = self._fetch_archive()
        df = pd.read_csv(io.StringIO(data_string),
                         sep=';',
                         decimal=',',
                         dtype={'Utgiftsområde': str,
                                'Utgiftsområde utfallsår': str,
                                'Anslag utfallsår': str,
                                'Anslag': str})
        df = df.pipe(self._clean)

        names = df[['esv_expenditure', 'esv_name', 'esv_allocation', 'esv_allocation_name']]
        df = df.drop(['esv_name', 'esv_allocation_name'], axis=1)

        expenditures = (names
                        .drop_duplicates(subset=['esv_expenditure'])
                        .dropna(subset=['esv_expenditure']))

        expenditures = expenditures.filter(items=['esv_expenditure', 'esv_name'])

        allocations = (names
                       .drop_duplicates(subset=['esv_allocation'])
                       .dropna(subset=['esv_allocation']))

        allocations = allocations.filter(items=['esv_allocation', 'esv_allocation_name'])
        allocations = allocations.rename(columns={'esv_allocation_name': 'esv_name'})

        self.data = {
            'df': df,
            'expenditures': expenditures,
            'allocations': allocations
        }

        return self.data
    
    def _clean(self, df):
        money_cols = ['Statens budget',
                      'Utfall',
                      'Ingående överföringsbelopp',
                      'Ändringsbudgetar',
                      'Indragningar',
                      'Utnyttjad del av medgivet överskridande',
                      'Anslagskredit',
                      'Utgående överföringsbelopp']

        for money_col in money_cols:
            df[money_col] = (df[money_col] * 1_000_000).round(0).astype('Int64')
        
        df['Anslag'] = df['Anslag'].str.replace(' ', '_').str.strip()

        df = df.drop(['Utgiftsområdesnamn utfallsår', 'Anslagsnamn utfallsår',
                      'Utgiftsområde utfallsår', 'Anslag utfallsår'], axis=1)
        
        df = df[df.Utgiftsområde.notnull()]

        concept_map = {x['name']: x['concept'] for x in esv_concepts}
        df = df.rename(columns=concept_map)

        return df

    def save(self, path, **kwargs):
        f2p = Frame2Package()
        f2p.add_data(self.data['df'], esv_concepts)
        f2p.update_entity('esv_expenditure', self.data['expenditures'])
        f2p.update_entity('esv_allocation', self.data['allocations'])

        f2p.to_package(path, **kwargs)


esv_concepts = [
    {
        'concept': 'year',
        'name': 'År',
        'concept_type': 'time',
    },
    {
        'concept': 'esv_expenditure',
        'name': 'Utgiftsområde',
        'concept_type': 'entity_domain',
        'description': 'Indelningsgrund för anslagen i statens budget.'
    },
    {
        'concept': 'esv_name',
        'name': 'Utgiftsområdesnamn',
        'concept_type': 'string',
        'description': 'Indelningsgrund för anslagen i statens budget.'
    },
    {
        'concept': 'esv_allocation',
        'name': 'Anslag',
        'concept_type': 'entity_domain',
        'description': 'Utgiftspost, underkategori till utgiftsområde.'
    },
    {
        'concept': 'esv_allocation_name',
        'name': 'Anslagsnamn',
        'concept_type': 'string',
        'description': 'Utgiftspost, underkategori till utgiftsområde.'
    },
    {
        'concept': 'esv_ingoing_transfer_amount',
        'name': 'Ingående överföringsbelopp',
        'concept_type': 'measure'
    },
    {
        'concept': 'esv_budget',
        'name': 'Statens budget',
        'concept_type': 'measure'
    },
    {
        'concept': 'esv_update_budgets',
        'name': 'Ändringsbudgetar',
        'concept_type': 'measure'
    },
    {
        'concept': 'esv_retractions',
        'name': 'Indragningar',
        'concept_type': 'measure',
        'description': 'Åtgärd enligt vilken regeringen får besluta att medel på ett anvisat anslag inte ska användas.'
    },
    {
        'concept': 'esv_exceed',
        'name': 'Utnyttjad del av medgivet överskridande',
        'concept_type': 'measure'
    },
    {
        'concept': 'esv_outcome',
        'name': 'Utfall',
        'concept_type': 'measure'
    },
    {
        'concept': 'esv_allocation_credit',
        'name': 'Anslagskredit',
        'concept_type': 'measure',
        'description': 'Ett tillåtet överskridande på ett ramanslag som förs över till kommande budgetår.'
    },
    {
        'concept': 'esv_outgoing_transfer_amount',
        'name': 'Utgående överföringsbelopp',
        'concept_type': 'measure'
    }
]