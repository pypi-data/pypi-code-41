import os
from glob import glob

import pandas as pd

from .utils import get_abspath
from .countries import identify_countries


class ArticleDropper():
    """Removes articles that for one reason or another are not relevant to
    include for classification or country identification purposes.

    Parameters
    ----------

    drop_brands : boolean, True by default
        Drop sub brands such as traveling sections.
    drop_debate : boolean, True by default
        Drop debate articles.
    drop_duplicates : boolean, True by default
        Drop articles with duplicated headline or lead.
    drop_len : boolean, True by default
        Drop by text length as defined by maxl, minl, maxh and minh.
    drop_mixed : boolean, True by default
        Drop articles with mixed content, such as news summaries.
    dropna : boolean, True by default
        Drop articles with missing headline or lead.
    maxl : int
        Max length of lead
    minl : int
        Min length of lead.
    maxh : int
        Max length of headline
    minh : int
        Min length of headline
    """

    def __init__(self, drop_brands=True, drop_debate=True,
                 drop_duplicates=True, drop_len=True,
                 drop_mixed=True, dropna=True,
                 maxl=400, minl=45, maxh=100, minh=10):
        self.drop_brands = drop_brands
        self.drop_debate = drop_debate
        self.drop_duplicates = drop_duplicates
        self.drop_len = drop_len
        self.drop_mixed = drop_mixed
        self.dropna = dropna
        self.maxl = maxl
        self.minl = minl
        self.maxh = maxh
        self.minh = minh

    def _drop_brands(self, df):
        brands = ['Allt om Resor', 'SvD Näringsliv']
        return df[~df.source.isin(brands)]

    def _drop_debate(self, df):
        df = df[~df.url.str.contains('svt.se/opinion/')]
        df = df[~df.url.str.contains('gp.se/nyheter/debatt/')]
        df = df[~df.url.str.contains('expressen.se/ledare/')]
        df = df[~df.lead.str.startswith('DEBATT')]
        df = df[~df.lead.str.startswith('ANALYS')]
        df = df[~df.lead.str.startswith('KOMMENTAR')]
        df = df[~df.lead.str.startswith('GÄST')]
        df = df[~df.lead.str.startswith('LEDARE')]
        df = df[~df.lead.str.startswith('KRÖNIKA')]
        df = df[~df.headline.str.startswith('LEDARE')]
        df = df[~df.headline.str.startswith('Ledare: ')]
        return df

    def _drop_duplicates(self, df):
        df = df.drop_duplicates(subset=['headline'])
        df = df.drop_duplicates(subset=['lead'])
        return df

    def _drop_len(self, df):
        df = df[df.lead.str.len() <= self.maxl]
        df = df[df.lead.str.len() >= self.minl]
        df = df[df.headline.str.len() <= self.maxh]
        df = df[df.headline.str.len() >= self.minh]
        return df

    def _drop_mixed(self, df):
        df = df[~df.lead.str.contains('detta hände när du sov')]
        df = df[~df.url.str.contains('medan-du-sov')]
        df = df[~df.url.str.contains('/tv-tabla/')]
        df = df[~df.url.str.contains('programid=438')]  # godmorgon världen
        df = df[~df.url.str.contains('programid=185')]  # Sisuradio
        return df

    def _dropna(self, df):
        return df.dropna(subset=['headline', 'lead'])

    def transform(self, df):
        """Execute all droppings on df."""
        if self.dropna:
            df = self._dropna(df)
        if self.drop_brands:
            df = self._drop_brands(df)
        if self.drop_debate:
            df = self._drop_debate(df)
        if self.drop_duplicates:
            df = self._drop_duplicates(df)
        if self.drop_len:
            df = self._drop_len(df)
        if self.drop_mixed:
            df = self._drop_mixed(df)

        return df


class CorpusReader():
    """Reads documents from disk."""
    def __init__(self):
        pass

    def docs(self):
        docs = list()
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(path, 'data/raw/')
        for doc in glob(f'{path}*.csv'):
            docs.append(pd.read_csv(doc))
        return pd.concat(docs)


class CorpusLoader():
    """The single source of truth for loading text documents."""

    cached_corpus_path = get_abspath('.cache/cached_corpus.csv')

    def __init__(self, use_cache=True):
        self._use_cache = use_cache

    def _cache_docs(self, df):
        df.to_csv(self.cached_corpus_path, index=False)

    def _identify_countries(self, df):
        df['countries'] = identify_countries(df.headline + ' ' + df.lead)
        return df

    def load_docs(self):
        if self._use_cache and self._cache_exists:
            return pd.read_csv(self.cached_corpus_path)
        else:
            return self._load_raw()

    def _load_raw(self):
        drop_cols = ['country', 'image', 'language', 'links', 'reference']
        reader = CorpusReader()
        df = reader.docs().drop(drop_cols, axis=1)

        dropper = ArticleDropper()
        df = dropper.transform(df)

        tagged = pd.read_csv(get_abspath('interim/tagged.csv'))
        df = pd.merge(df, tagged[['cat', 'url']], left_on='url',
                      right_on='url', how='left')

        df = self._identify_countries(df)
        df.countries = df.countries.apply(lambda x: ','.join(x))

        self._cache_docs(df)
        return pd.read_csv(self.cached_corpus_path)

    @property
    def _cache_exists(self):
        return os.path.exists(self.cached_corpus_path)
