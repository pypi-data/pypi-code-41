import io
import re
import json
import shutil
import pathlib
import calendar
import requests
from bs4 import BeautifulSoup
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
import numpy as np
from datasetmaker.entity import Country
from datasetmaker.models import Client
from datasetmaker.indicator import concepts


base_url = "https://en.wikipedia.org/wiki"


class Wikipedia(Client):
    @property
    def indicators(self):
        global concepts
        return concepts[concepts.source == ''].concept.tolist()   

    def _map_pages(self, concept_names):
        pages = []
        for name in concept_names:
            if name == 'country':
                continue
            page = concepts[concepts.concept == name].context.iloc[0]
            page = json.loads(page).get('page')
            pages.append(page)
        return set(pages)

    def get(self, indicators=None, years=None):
        pages = ['List_of_next_general_elections',
                 'List_of_current_heads_of_state_and_government',
                 'Visa']
        frames = []
        for page in pages:
            frame = scrapers[page]()
            frames.append(frame)

        temp = pd.merge(frames[0], frames[1], on='country', how='outer')
        frames = [frames[-1], temp]
        df = pd.concat(frames, sort=True)
        self.data = df
        return df

    def save(self, path, **kwargs):
        global concepts

        path = pathlib.Path(path)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir()

        concepts_ = concepts[(concepts.source == 'wikipedia') | (concepts.concept == 'country')]
        concepts_ = concepts_[['concept', 'concept_type', 'name', 'domain']]
        concepts_.to_csv(path / 'ddf--concepts.csv', index=False)

        countries = self.data[['wikipedia_parl_prev', 'wikipedia_parl_next',
                               'wikipedia_parl_term', 'wikipedia_pres_prev',
                               'wikipedia_pres_next', 'wikipedia_pres_term',
                               'country', 'wikipedia_head_state_title',
                               'wikipedia_head_state_name', 'wikipedia_head_gov_title',
                               'wikipedia_head_gov_name']]
        countries = countries[sorted(countries.columns)].dropna(subset=['country'])
        countries.to_csv(path / 'ddf--entities--country.csv', index=False)

        rec = self.data[['wikipedia_visa_reciprocity',
                          'wikipedia_visa_country_from',
                          'wikipedia_visa_country_to']]

        rec.columns = ['wikipedia_visa_reciprocity',
                        'wikipedia_flow.wikipedia_visa_country_from',
                        'wikipedia_flow.wikipedia_visa_country_to']

        rec = rec.dropna(subset=['wikipedia_visa_reciprocity'])

        rec.to_csv(
            path / 'ddf--datapoints--wikipedia_visa_reciprocity--by--wikipedia_visa_country_from--wikipedia_visa_country_to.csv', index=False)

        req = self.data[['wikipedia_visa_requirement',
                          'wikipedia_visa_country_from',
                          'wikipedia_visa_country_to']]

        req.columns = ['wikipedia_visa_requirement',
                        'wikipedia_flow.wikipedia_visa_country_from',
                        'wikipedia_flow.wikipedia_visa_country_to']

        req = req.dropna(subset=['wikipedia_visa_requirement'])

        req.to_csv(
            path / 'ddf--datapoints--wikipedia_visa_requirement--by--wikipedia_visa_country_from--wikipedia_visa_country_to.csv', index=False)

        stay = self.data[['wikipedia_visa_allowed_stay',
                          'wikipedia_visa_country_from',
                          'wikipedia_visa_country_to']]

        stay.columns = ['wikipedia_visa_allowed_stay',
                        'wikipedia_flow.wikipedia_visa_country_from',
                        'wikipedia_flow.wikipedia_visa_country_to']

        stay = stay.dropna(subset=['wikipedia_visa_allowed_stay'])

        stay.to_csv(
            path / 'ddf--datapoints--wikipedia_visa_allowed_stay--by--wikipedia_visa_country_from--wikipedia_visa_country_to.csv', index=False)

        (self.data
            .wikipedia_visa_requirement
            .dropna()
            .drop_duplicates()
            .sort_values()
            .to_csv(path / 'ddf--entities--wikipedia_visa_requirement.csv',
                    index=False,
                    header=True))

        meta = package.create_datapackage(path, **kwargs)
        dump_json(path / 'datapackage.json', meta)

        return self


def fetch_elections():
    url = f'{base_url}/List_of_next_general_elections'
    return requests.get(url).text


def scrape_elections():
    html = fetch_elections()
    tables = pd.read_html(io.StringIO(html), match="Parliamentary")
    df = pd.concat(tables, sort=True)

    cols = [
        "country",
        "wikipedia_fair",
        "wikipedia_gdp",
        "wikipedia_ihdi",
        "wikipedia_power",
        "wikipedia_parl_prev",
        "wikipedia_parl_next",
        "wikipedia_parl_term",
        "wikipedia_pop",
        "wikipedia_pres_prev",
        "wikipedia_pres_next",
        "wikipedia_pres_term",
        "wikipedia_status",
    ]

    keep_cols = [
        "country",
        "wikipedia_parl_prev",
        "wikipedia_parl_next",
        "wikipedia_parl_term",
        "wikipedia_pres_prev",
        "wikipedia_pres_next",
        "wikipedia_pres_term",
    ]

    df.columns = cols
    df = df[keep_cols]

    # Remove countries with no next election info
    df = df[df.wikipedia_parl_next.notnull()]

    # Remove European Union
    df = df[df.country != 'European Union']

    # Convert previous election to datetime
    df["wikipedia_parl_prev"] = pd.to_datetime(df.wikipedia_parl_prev)

    # Remove footnotes
    df.wikipedia_parl_term = df.wikipedia_parl_term.str.split("[", expand=True)[0]
    df.wikipedia_pres_term = df.wikipedia_pres_term.str.split("[", expand=True)[0]

    df.wikipedia_parl_next = parse_wikipedia_time(df.wikipedia_parl_next)
    df.wikipedia_pres_next = parse_wikipedia_time(df.wikipedia_pres_next)

    df.wikipedia_parl_term = df.wikipedia_parl_term.str.split(" ", expand=True)[0]
    df.country = df.country.replace("Korea", "South Korea")
    df["iso_3"] = df.country.map(Country.name_to_id())

    df = df.drop('country', axis=1).rename(columns={'iso_3': 'country'})
    df = df.dropna(subset=["country"])

    return df


def parse_wikipedia_time(ser):
    year = ser.str[-4:]
    month = ser.str.extract("(\D+)")[0]
    month = month.str.strip()
    day = ser.str.extract("(\d{1,2}) ")[0]

    month_names = list(calendar.month_name)

    month = month.apply(
        lambda x: str(month_names.index(x)).zfill(
            2) if x in month_names else np.nan
    )

    month = month.astype(str).str.replace("nan", "")
    day = day.astype(str).str.zfill(2).str.replace("nan", "")

    ser = year + '-' + month + '-' + day

    ser = ser.str.replace("-nan", "")
    ser = ser.str.replace('-+$', '', regex=True)
    return ser


def fetch_visas():
    base_url = 'https://en.wikipedia.org'

    url_lists = ['w/index.php?title=Category:Visa_requirements_by_nationality',
                ('w/index.php?title=Category:Visa_requirements_by_nationality'
                '&pagefrom=Turkey%0AVisa+requirements+for+Turkish+citizens')]

    url_lists = [f'{base_url}/{url}' for url in url_lists]

    excluded = ['Visa_requirements_for_Abkhaz_citizens',
        'Visa_requirements_for_EFTA_nationals',
        'Visa_requirements_for_Estonian_non-citizens',
        'Visa_requirements_for_European_Union_citizens',
        'Visa_requirements_for_Latvian_non-citizens',
        'Visa_requirements_for_Artsakh_citizens',
        'Visa_requirements_for_Somaliland_citizens',
        'Visa_requirements_for_South_Ossetia_citizens',
        'Template:Timatic_Visa_Policy',
        'Visa_requirements_for_Transnistrian_citizens',
        'Template:Visa_policy_link']

    def get_country_links():
        links = []
        for url in url_lists:
            r = requests.get(url)
            html = BeautifulSoup(r.text, features='lxml')
            els = html.select('.mw-category-group a')
            links.extend([f"{base_url}/{x.attrs['href'][1:]}" for x in els])
        return links

    def get_country(url):
        title = url.split('/')[-1]
        table = (requests.get(url).text, title)
        return table

    tables = [get_country(x) for x in get_country_links()]
    return tables


def scrape_visas():
    tables = fetch_visas()
    frames = []
    for table, title in tables:
        try:
            frame = pd.read_html(io.StringIO(table),
                                 match='Visa requirement',
                                 flavor='lxml')
            if len(frame) > 1:
                frame = [x for x in frame if 'Visa requirement' in x.columns][0]
            else:
                frame = frame[0]
            frame['Title'] = title
            frames.append(frame)
        except (ImportError, ValueError):
            continue

    def create_dataframe(tables):
        clean_tables = []
        for t in tables:
            if type(t) is pd.DataFrame and t.shape[0] > 5:
                clean_tables.append(t)
        return pd.concat(clean_tables, sort=True)

    df = create_dataframe(frames)
    df = df.dropna(how='all', axis=1)
    df['Title'] = df['Title'].str.replace('Visa_requirements_for_', '')
    df = df.replace('\[[0-9]+\]', '', regex=True)
    df['Title'] = df['Title'].str.replace('%C3%A9', 'é')

    df['Title'] = (df['Title']
        .str.replace('_', ' ')
        .str.replace(' citizens', '')
        .str.replace('citizens of North Macedonia', 'North Macedonia')
        .str.replace('Chinese of ', '')
        .replace('Democratic Republic of the Congo', 'Democratic Republic of Congo')
        .replace('Republic of the Congo', 'Republic of Congo')
        .replace('holders of passports issued by the ', '')
        .str.strip())

    df = df[df.Title != 'British Nationals (Overseas)']
    df = df[df.Title != 'British Overseas']
    df = df[df.Title != 'British Overseas Territories']
    df = df[df.Title != 'holders of passports issued by the Sovereign Military Order of Malta']
    df = df[df['Title'] != 'crew members']

    if 'Notes' in df:
        df['Notes'] = df['Notes'].fillna(df['Notes (excluding departure fees)'])

    df = df.drop(['Notes (excluding departure fees)'], axis=1, errors='ignore')

    df['Visa requirement'] = (df['Visa requirement']
        .str.lower()
        .replace('evisa', 'electronic visa')
        .replace('e-visa', 'electronic visa')
        .replace('evisa required', 'electronic visa')
        .replace('electronic visatr', 'electronic visa')
        .str.replace('<', '', regex=False)
        .str.replace('\[[Nn]ote 1\]', '')
        .str.replace('[dubious – discuss]', '', regex=False)
        .replace('electronic authorization system', 'electronic authorization')
        .replace('electronic authorization', 'electronic authorisation')
        .replace('electronic travel authorisation', 'electronic authorisation')
        .replace('electronic travel authority', 'electronic authorisation')
        .replace('electronic travel authorization', 'electronic travel authorisation')
        .replace('visa not required (conditions apply)', 'visa not required (conditional)')
        .replace('visa on arrival /evisa', 'visa on arrival / evisa')
        .replace('visitor\'s permit on arrival', 'visitor permit on arrival')
        .replace('visitor\'s permit is granted on arrival', 'visitor permit on arrival')
        .replace('evisa/entri', 'evisa / entri')
        .str.strip())

    df['_days'] = df['Allowed stay'].str.extract('([0-9]+) ?q?day', flags=re.I)[0]
    df['_months'] = df['Allowed stay'].str.extract('([0-9]+) mon?th', flags=re.I)[0]
    df['_weeks'] = df['Allowed stay'].str.extract('([0-9]+) week', flags=re.I)[0]
    df['_years'] = df['Allowed stay'].str.extract('([0-9]+) year', flags=re.I)[0]
    df['_fom'] = df['Allowed stay'].str.lower().str.extract('(freedom of movement)')[0]
    df['_unl'] = df['Allowed stay'].str.lower().str.extract('(unlimited)')[0]

    df['_days'] = (df['_days'].astype(float)
        .fillna(df._weeks.astype(float) * 7)
        .fillna(df._months.astype(float) * 30)
        .fillna(df._years.astype(float) * 365)
        .fillna(df._fom)
        .fillna(df._unl))

    df = df.drop(['_months', '_weeks', '_years', '_fom', '_unl'], axis=1)
    df = df.rename(columns={'_days': 'Allowed stay days'})
    df = df.drop(['Allowed stay', 'Notes'], axis=1, errors='ignore')

    if 'Reciprocality' in df:
        df.wikipedia_visa_reciprocity = df.wikipedia_visa_reciprocity.fillna(df.Reciprocality)
        df = df.drop(['Reciprocality'], axis=1)
    
    if 'Reciprocity' not in df:
        df['Reciprocity'] = None
    else:
        df.Reciprocity = (df.Reciprocity
                            .replace('√', True)
                            .replace('Yes', True)
                            .replace('X', False)
                            .replace('✓', True))

    df = df.rename(columns={
        'Country': 'wikipedia_visa_country_to',
        'Title': 'wikipedia_visa_country_from',
        'Reciprocity': 'wikipedia_visa_reciprocity',
        'Visa requirement': 'wikipedia_visa_requirement',
        'Allowed stay days': 'wikipedia_visa_allowed_stay'
    })

    df.wikipedia_visa_requirement = df.wikipedia_visa_requirement.str.replace(' ', '_')

    df.wikipedia_visa_country_from = df.wikipedia_visa_country_from.str.replace('excluding some Overseas territories', '')
    df.wikipedia_visa_country_to = df.wikipedia_visa_country_to.str.replace('excluding some Overseas territories', '')
    df.wikipedia_visa_country_from = df.wikipedia_visa_country_from.str.replace(' and territories', '')
    df.wikipedia_visa_country_to = df.wikipedia_visa_country_to.str.replace(' and territories', '')
    df.wikipedia_visa_country_from = df.wikipedia_visa_country_from.str.replace(' and external territories', '')
    df.wikipedia_visa_country_to = df.wikipedia_visa_country_to.str.replace(' and external territories', '')

    from_map = Country.denonym_to_id()
    from_map.update(Country.name_to_id())
    df['wikipedia_visa_country_from'] = df['wikipedia_visa_country_from'].map(from_map)
    df['wikipedia_visa_country_to'] = df['wikipedia_visa_country_to'].map(
        Country.name_to_id())

    return df


def scrape_heads_of_state_and_government():
    url = f'{base_url}/List_of_current_heads_of_state_and_government'
    tables = pd.read_html(url)
    df = pd.concat(tables[1:4], sort=True)
    df = df.drop('Also claimed by', axis=1)
    df['State'] = df['State'].fillna(df['State/Government'])
    df = df.drop('State/Government', axis=1)
    df.columns = ['wikipedia_head_gov', 'wikipedia_head_state', 'country']
    df['country'] = df.country.map(Country.name_to_id())

    head_state = (df
                  .wikipedia_head_state
                  .str.replace('\xa0', ' ')
                  .str.split('\[α\]', expand=True)[0]
                  .str.split('\[δ\]', expand=True)[0]
                  .str.split('\[γ\]', expand=True)[0]
                  .str.split('\[κ\]', expand=True)[0]
                  .str.split(' – ', n=-1, expand=True))

    df['wikipedia_head_state_title'] = head_state[0].str.strip()
    df['wikipedia_head_state_name'] = head_state[1].str.strip()

    head_gov = (df
                .wikipedia_head_gov
                .str.replace('\xa0', ' ')
                .str.split('\[α\]', expand=True)[0]
                .str.split('\[δ\]', expand=True)[0]
                .str.split('\[γ\]', expand=True)[0]
                .str.split('\[κ\]', expand=True)[0]
                .str.split(' – ', n=-1, expand=True))

    df['wikipedia_head_gov_title'] = head_gov[0].str.strip()
    df['wikipedia_head_gov_name'] = head_gov[1].str.strip()

    df = df.drop(['wikipedia_head_state', 'wikipedia_head_gov'], axis=1)
    df = df.sort_values('country')

    return df


scrapers = {
    'List_of_next_general_elections': scrape_elections,
    'List_of_current_heads_of_state_and_government': scrape_heads_of_state_and_government,
    'Visa': scrape_visas
}
