import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy


def mean_score_decrease(X_train, y_train, model, plot=False, topk=None, n_fold=3, normalize=False):
    """
    Function to calculate mean score decrease. Mean score decrease is model agnostic because it perform a random
    permutation on each of the input columns then collects the score decrease caused by each columns.


    == Example usage ==
    from jcopml.feature_importance import mean_score_decrease
    df_imp = mean_score_decrease(X_train, y_train, model, plot=True)
    df_imp = mean_score_decrease(X_train, y_train, model, plot=True, topk=10)


    == Arguments ==
    X_train: pandas DataFrame
        training input features

    y_train: pandas Series
        training labels

    model: scikit-learn pipeline or estimator
        trained scikit-learn pipeline or estimator

    plot: bool
        show feature importance barplot

    topk: int
        number or k most important feature to show in the barplot

    n_fold: int
        number of permutation to perform before aggregating the mean score decrease

    normalize: bool
        perform minmax scaling, then normalize the importance so that they summed up to 1


    == Return ==
    pandas DataFrame with the features and importance
    """
    model = deepcopy(model)

    init_score = model.score(X_train, y_train)
    score = {}
    for col in X_train.columns:
        score[col] = []
        for i in range(n_fold):
            X_tmp = X_train.copy()
            X_tmp[col] = X_tmp[col].sample(frac=1, random_state=42+i).values
            score[col].append(model.score(X_tmp, y_train))
    score = {col: init_score - np.mean(score[col]) for col in X_train.columns}

    cols = [k for k, v in score.items()]
    imp = [v for k, v in score.items()]
    df_imp = pd.DataFrame({"feature": cols, "importance": imp}).sort_values("importance", ascending=False)

    if normalize:
        df_imp.importance = df_imp.importance.transform(lambda x: (x - x.min()) / (x.max() - x.min()))
        df_imp.importance = df_imp.importance.transform(lambda x: x / x.sum())

    if topk:
        df_imp = df_imp.head(topk)

    if plot:
        plt.figure(figsize=(15, 5))
        plt.bar(range(len(df_imp)), df_imp.importance, color='b')
        plt.xticks(range(len(df_imp)), df_imp.feature, rotation=45, horizontalalignment='right')
        plt.ylabel('importance')
        plt.title("Mean Score Decrease", fontsize=14);
    return df_imp
