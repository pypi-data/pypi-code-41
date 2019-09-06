import io
import os
import shutil
import requests
import zipfile
import pandas as pd
from ddf_utils import package
from ddf_utils.io import dump_json
from datasetmaker.models import Client
from datasetmaker.indicator import concepts
from datasetmaker.entity import get_entity_frame
from datasetmaker.utils import ddfify


class ValforskClient(Client):
    def get(self, indicators=None, periods=None):
        url = "https://www.dropbox.com/sh/8hdmg83o0o78ovn/AABdmOuIgpiOs99IMrgUTsHra?dl=1"

        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))

        path = "polls"

        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        z.extractall(path)

        mama = pd.read_csv("polls/trender/utfil_bw15_mama.csv")
        polls = pd.read_csv("polls/polls.csv")
        polls = self._clean_polls(polls)

        self.mama = mama
        self.polls = polls

    def _clean_polls(self, df):
        """Clean dataframe with raw polling data"""

        # Calculate date between start an end
        df.coll_per_start = pd.to_datetime(df.coll_per_start)
        df.coll_per_end = pd.to_datetime(df.coll_per_end)
        polls_length = df.coll_per_end - df.coll_per_start
        df['date'] = (df.coll_per_start + (polls_length / 2)).dt.date

        # Drop redundant columns
        df = df.drop(['coll_per_start', 'coll_per_end'], axis=1)

        # Melt party columns
        party_cols = ['m', 'l', 'c', 'kd', 's', 'v',
                      'mp', 'sd', 'fi', 'pp', 'oth', 'dk']
        df = df.melt(id_vars=['pollster', 'date', 'samplesize'],
                     value_vars=party_cols,
                     var_name='party',
                     value_name='valforsk_opinion_value')

        df = df.rename(columns={'samplesize': 'valforsk_samplesize'})
        df.pollster = df.pollster.str.lower()
        return df

    def save(self, path, **kwargs):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        valforsk_concepts = concepts[(concepts.source == 'valforsk') |
                                     (concepts.concept.isin(['party',
                                                             'date',
                                                             'pollster',
                                                             'name']))]
        valforsk_concepts.to_csv(os.path.join(
            path, 'ddf--concepts.csv'), index=False)

        parties_ontology = get_entity_frame('party')
        self.polls.party = self.polls.party.map(
            parties_ontology[['party', 'abbr']].set_index('abbr').party.to_dict())

        op_name = ('ddf--datapoints--valforsk_opinion_value--'
                   'by--pollster--party--date.csv')
        op_df = self.polls.drop('valforsk_samplesize', axis=1)
        op_df.to_csv(os.path.join(path, op_name), index=False)

        ss_name = ('ddf--datapoints--valforsk_samplesize--'
                   'by--pollster--party--date.csv')
        ss_df = self.polls.drop('valforsk_opinion_value', axis=1)
        ss_df.to_csv(os.path.join(path, ss_name), index=False)

        parties = self.polls[['party']].drop_duplicates()
        parties_ontology = get_entity_frame('party')
        parties = parties.merge(parties_ontology, on='party')
        parties.to_csv(
            os.path.join(path, 'ddf--entities--party.csv'), index=False)

        pollsters = self.polls[['pollster']].drop_duplicates()
        pollsters_ontology = get_entity_frame('pollster')
        pollsters = pollsters.merge(pollsters_ontology, on='pollster')
        pollsters.to_csv(
            os.path.join(path, 'ddf--entities--pollster.csv'), index=False)

        ddfify(path,
               name='valforsk',
               source='Valforskningsprogrammet',
               default_measure='valforsk_opinion_value',
               default_primary_key=['pollster', 'party', 'date'],
               topics=['politics', 'sweden'])
