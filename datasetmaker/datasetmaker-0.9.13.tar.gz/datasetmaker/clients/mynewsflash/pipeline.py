import os
import pickle
import pathlib
import pandas as pd
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from .transformers import (
    TextMerger,
    TextCleanTransformer,
    Tokenizer)

from datasetmaker.path import ROOT_DIR


def do_nothing(x):
    return x


token_pipe = Pipeline([
    ('merger', TextMerger(['headline', 'lead'], sep='. ')),
    ('cleaner', TextCleanTransformer()),
    ('tokenizer', Tokenizer())
])

clf_pipe = OneVsRestClassifier(Pipeline([
    ('vect', TfidfVectorizer(tokenizer=do_nothing, preprocessor=None,
                             lowercase=False,
                             min_df=2,
                             ngram_range=(1, 2))),
    ('clf', LogisticRegression(C=1000000,
                               intercept_scaling=0.05, dual=False, solver='liblinear'))
]))


pipe_factory = Pipeline([('token', token_pipe), ('clf', clf_pipe)])

classes = ['accidents', 'crime', 'culture', 'economy',
           'nature', 'politics', 'protests', 'science', 'sports']


def create_pipeline(train=False):
    from .train_data import data
    tagged = pd.DataFrame(data)
    model_path = pathlib.Path(ROOT_DIR) / 'assets' / 'news_model.pk'

    if train:
        y = tagged[classes].values
        pipe_factory.fit(tagged, y)
        pickle.dump(pipe_factory, open(model_path, 'wb'))
        return pipe_factory
    else:
        pipe = pickle.load(open(model_path, 'rb'))
        return pipe
