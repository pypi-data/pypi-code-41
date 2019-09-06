import re
import os

import pandas as pd
from spacy.lang.sv import Swedish, STOP_WORDS, lemmatizer
from spacy.attrs import ORTH, LEMMA
from sklearn.base import BaseEstimator, TransformerMixin

from .stop_words import CUSTOM_STOPS
from .config import COUNTRY_TOKEN, DIGIT_TOKEN, WEEKDAY_TOKEN
from .bigrams import BIGRAMS
from .country_data import countries


class TextCleanTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def _replace_digits(self, docs):
        docs = docs.str.replace(r'\d', DIGIT_TOKEN)
        alpha_digits = [r'\b[Tt]vå\b', r'\b[Tt]re\b', r'\b[Ff]yra\b',
                        r'\b[Ff]em\b', r'\b[Ss]ju\b', r'\b[Åå]tta\b',
                        r'\b[Nn]io\b', r'\b[Tt]io\b', r'\b[Ee]lva\b',
                        r'\b[Tt]olv\b', r'\b[Tt]retton\b', r'\b[Ff]orton\b']
        alpha_digits_pat = '|'.join(alpha_digits)
        docs = docs.str.replace(alpha_digits_pat, DIGIT_TOKEN)
        return docs

    def _replace_weekdays(self, docs):
        weekdays = [r'\b[Mm]åndags?\b', r'\b[Tt]isdags?\b', r'\b[Oo]nsdags?\b',
                    r'\b[Tt]orsdags?\b', r'\b[Ff]redags?\b',
                    r'\b[Ll]ördags?\b', r'\b[Ss]öndags?\b',
                    r'\b[Mm]åndagens?\b', r'\b[Tt]isdagens?\b',
                    r'\b[Oo]nsdagens?\b', r'\b[Tt]orsdagens?\b',
                    r'\b[Ff]redagens?\b', r'\b[Ll]ördagens?\b',
                    r'\b[Ss]öndagens?\b']

        weekday_pat = '|'.join(weekdays)
        docs = docs.str.replace(weekday_pat, WEEKDAY_TOKEN)
        return docs

    def _replace_country_names(self, docs):
        # path = os.path.dirname(os.path.abspath(__file__))
        # path = os.path.join(path, 'countries.csv')
        # country_names = pd.read_csv(path)[['iso_3', 'name_swe']]
        global countries
        country_names = pd.DataFrame(countries)[['iso_3', 'name_swe']]

        country_names_pat = r's?|'.join(country_names.name_swe.values) + r's?'
        docs = docs.str.replace(country_names_pat, COUNTRY_TOKEN)
        return docs

    def _replace_non_breaking_space(self, docs):
        docs = docs.str.replace('\xa0', ' ')
        return docs

    def _remove_prefixes(self, docs):
        prefixes = [r'VIDEO \|', r'LIVE:', r'Live:' r'TT-FLASH:', r'FLASH:',
                    r'Uppgifter:', r'JUST NU:', r'AFP:']

        for prefix in prefixes:
            docs = docs.str.replace(prefix, '')

        return docs

    def _remove_org_names(self, docs):
        org_names = [r'\(SvD Premium\)', r'\(SvD Perfect Guide\)',
                     r'\(SvD Börsplus\)', 'Vetenskapsradion', r'svt\.se']

        for org_name in org_names:
            docs = docs.str.replace(org_name, '')

        return docs

    def _replace_ambiguous_terms(self, docs):
        terms = [(r'\bIS\b', 'Isis')]

        for before, after in terms:
            docs = docs.str.replace(before, after)
        return docs

    def fit(self, X, y=None):
        return self

    def transform(self, docs):
        if type(docs) is list:
            docs = pd.Series(docs)
        if not isinstance(docs, pd.core.series.Series):
            raise ValueError('Must pass either list or pandas Series')

        docs = self._replace_non_breaking_space(docs)
        docs = self._replace_digits(docs)
        docs = self._replace_weekdays(docs)
        docs = self._replace_country_names(docs)
        docs = self._replace_ambiguous_terms(docs)
        docs = self._remove_prefixes(docs)
        docs = self._remove_org_names(docs)

        return docs


class TextMerger(BaseEstimator, TransformerMixin):
    def __init__(self, cols, sep):
        self.cols = cols
        self.sep = sep

    def fit(self, X, y=None):
        return self

    def transform(self, docs):
        if isinstance(docs, pd.core.series.Series):
            return docs
        elif isinstance(docs, list):
            return docs
        elif isinstance(docs, pd.core.frame.DataFrame):
            return docs[self.cols[0]] + self.sep + docs[self.cols[1]]
        else:
            raise ValueError('Must pass iterable or pandas Dataframe')


class TextStats(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, docs):
        for doc in docs:
            yield {
                'length': len(doc)
            }


class Tokenizer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, docs):
        if type(docs) is list:
            docs = pd.Series(docs)
        if not isinstance(docs, pd.core.series.Series):
            raise ValueError('Must pass either list or pandas Series')

        docs = self._make_bigrams(docs)

        STOP_WORDS.clear()  # remove spacy's default stop words
        STOP_WORDS.update(CUSTOM_STOPS)

        # Remove weird lemmas from spacy
        bad_lemmas = ['gäng', 'handla', 'handlas', 'år', 'åre']
        for lemma in bad_lemmas:
            try:
                lemmatizer.LOOKUP.pop(lemma)
            except KeyError:
                continue

        lemmatizer.LOOKUP['gänget'] = 'gäng'
        lemmatizer.LOOKUP['gängets'] = 'gäng'
        lemmatizer.LOOKUP['bitcoins'] = 'bitcoin'

        nlp = Swedish()
        spacy_tokenizer = Swedish().Defaults.create_tokenizer(nlp)

        # Prevent spacy from tokenizing individual digits
        for i in range(1, 8):
            case = DIGIT_TOKEN * i
            spacy_tokenizer.add_special_case(case, [{ORTH: case, LEMMA: case}])

        docs = docs.apply(spacy_tokenizer)
        # TODO: Speed up below line
        # docs = docs.apply(self._merge_digits)
        docs = docs.apply(self._tokenize)

        return docs

    def _make_bigrams(self, docs):
        for bigram in BIGRAMS:
            docs = docs.str.replace(bigram, r'\1_\2',
                                    flags=re.I)
        return docs

    def _merge_digits(self, doc):
        # Merge digit-string combos into single tokens
        for i in range(1, 8):
            case = DIGIT_TOKEN * i
            spans = [m.span() for m in re.finditer(case + r'[-\w]+', doc.text)]
            for start, end in spans:
                doc.merge(start, end)
        return doc

    def _tokenize(self, doc):
        return [x.lemma_.lower() for x in doc if
                not x.is_punct and not x.is_stop and not x.is_space]
