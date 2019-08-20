# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

from sklearn.datasets import load_iris

data = load_iris()
X = data.data
y = data.target

search_config = {
    "xgboost.XGBClassifier": {
        "n_estimators": range(1, 20, 1),
        "max_depth": range(1, 11),
        "learning_rate": [1e-3, 1e-2, 1e-1, 0.5, 1.0],
        "min_child_weight": range(1, 21),
    }
}


def test_xgboost():
    from hyperactive import RandomSearchOptimizer

    opt = RandomSearchOptimizer(search_config, 3)
    opt.fit(X, y)
    opt.predict(X)
    opt.score(X, y)


def test_xgboost_score():
    from hyperactive import RandomSearchOptimizer

    ml_scores = ["accuracy_score"]

    for score in ml_scores:
        opt = RandomSearchOptimizer(search_config, 3, metric=score)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


def test_xgboost_loss():
    from hyperactive import RandomSearchOptimizer

    ml_losses = [
        "mean_absolute_error",
        "mean_squared_error",
        "mean_squared_log_error",
        "median_absolute_error",
    ]

    for loss in ml_losses:
        opt = RandomSearchOptimizer(search_config, 3, metric=loss)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


"""
def _test_xgboost_n_jobs():
    from hyperactive import RandomSearchOptimizer

    n_jobs_list = [1, 2, 3, 4]
    for n_jobs in n_jobs_list:
        opt = RandomSearchOptimizer(search_config, 3, n_jobs=n_jobs)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)
"""


def test_xgboost_n_iter():
    from hyperactive import RandomSearchOptimizer

    n_iter_list = [0, 1, 3, 10]
    for n_iter in n_iter_list:
        opt = RandomSearchOptimizer(search_config, n_iter)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


def test_xgboost_cv():
    from hyperactive import RandomSearchOptimizer

    cv_list = [0.1, 0.5, 0.9, 2, 4]
    for cv in cv_list:
        opt = RandomSearchOptimizer(search_config, 3, cv=cv)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


def test_xgboost_verbosity():
    from hyperactive import RandomSearchOptimizer

    verbosity_list = [0, 1, 2]
    for verbosity in verbosity_list:
        opt = RandomSearchOptimizer(search_config, 3, verbosity=verbosity)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


def test_xgboost_random_state():
    from hyperactive import RandomSearchOptimizer

    random_state_list = [None, 0, 1, 2]
    for random_state in random_state_list:
        opt = RandomSearchOptimizer(search_config, 3, random_state=random_state)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


def test_xgboost_warm_start():
    from hyperactive import RandomSearchOptimizer

    warm_start = {"sklearn.tree.DecisionTreeClassifier": {"max_depth": [1]}}

    warm_start_list = [None, warm_start]
    for warm_start in warm_start_list:
        opt = RandomSearchOptimizer(search_config, 3, warm_start=warm_start)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


def test_xgboost_memory():
    from hyperactive import RandomSearchOptimizer

    memory_list = [False, True]
    for memory in memory_list:
        opt = RandomSearchOptimizer(search_config, 3, memory=memory)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)


def test_xgboost_scatter_init():
    from hyperactive import RandomSearchOptimizer

    scatter_init_list = [False, 2, 3, 4]
    for scatter_init in scatter_init_list:
        opt = RandomSearchOptimizer(search_config, 3, scatter_init=scatter_init)
        opt.fit(X, y)
        opt.predict(X)
        opt.score(X, y)
