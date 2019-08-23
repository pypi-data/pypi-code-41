from typing import Dict, Any

from algoneer.algorithm.sklearn import SklearnAlgorithm
from algoneer.algorithm import Algorithm

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB

algorithms : Dict[str, Any]= {
    'random-forest' : RandomForestRegressor,
    'logistic-regression' : LogisticRegression,
    'linear-regression' : LinearRegression,
    'k-nearest-neighbors' : KNeighborsClassifier,
    'decision-tree' : DecisionTreeClassifier,
    'gaussian-nb' : GaussianNB
}

default_args : Dict[str, Dict[str, Any]]= {
    'logistic-regression' : {
        'solver' : 'lbfgs',
        'multi_class' : 'auto',
    },
    'random-forest' : {
        'n_estimators' : 100,
    },
}

def get_algorithm(type : str, **kwargs) -> Algorithm:
    d : Dict[str, Dict[str, Any]] = {}
    kw : Dict[str, Dict[str, Any]]= default_args.get(type, d).copy()
    kw.update(kwargs)
    return SklearnAlgorithm(algorithms[type], kwargs=kw)
