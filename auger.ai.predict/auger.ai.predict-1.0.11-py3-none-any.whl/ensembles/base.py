import numpy as np

# from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import LabelEncoder

from auger_ml.ensembles.utils import get_pipelines


class BaseEnsemble(object):
    """ Base class for all Ensemble classes.

    Note: this class should not be used directly -> Use derived classes instead.

    Parameters
    ----------
    pipelines : list of pipelines, which is used for ensemble.
    """
    def __init__(self, options, pipelines, classification, params):
        from auger_ml.preprocessors.space import pspace_get_fold_group        

        self.pipelines = get_pipelines(pipelines, options)
        self.pipelines_fold_group = [ pspace_get_fold_group(p['name'], options.get('timeSeriesFeatures')) for p in pipelines]
        self.classification = classification
        self._params = params
        self.le = LabelEncoder()
        self.options = options
        self._num_features = None

    def fit(self, x, y):
        """ Fit defined pipelines.

        Parameters
        ----------
        x : {array-like, matrix}, shape = [n_samples, n_features].

        y : array-like, shape = [n_samples] -> target values.

        Returns
        -------
        self : object
        """

        res = []
        self._num_features = x[self.pipelines_fold_group[0]].shape[1]
        for idx, p in enumerate(self.pipelines):
            x_fold = x[self.pipelines_fold_group[idx]]
            y_fold = y[self.pipelines_fold_group[idx]]
            if self.classification:
                y_fold = self.le.fit_transform(y_fold)

            res.append( p.fit(x_fold, y_fold))             

        self.pipelines = res
        return self

    def get_params(self, deep=False):
        return self._params

    def _predict(self, x):
        """ Collect predictions as labels for defined pipelines
        within an array-like, shape = [n_pipelines, n_samples]. """
        res = []
        for idx, p in enumerate(self.pipelines):
            x_fold = x[self.pipelines_fold_group[idx]]
            pred = p.predict(x_fold)
            if len(np.asarray(pred).shape) > 0:
                res.append(pred)

        return np.asarray(res)

    def _predict_proba(self, x):
        """ Collect predictions as probabilities for defined pipelines
        within an array-like, shape = [n_pipelines, n_samples, n_classes]. """
        res = []
        for idx, p in enumerate(self.pipelines):
            x_fold = x[self.pipelines_fold_group[idx]]
            try:
                res.append(p.predict_proba(x_fold))
            except AttributeError as e:
                res.append(p._predict_proba(x_fold))
                        
        return np.asarray(res)

    def __len__(self):
        """ Returns the number of pipelines within the ensemble."""
        return len(self.pipelines)

    def __getitem__(self, index):
        """ Returns the index'th pipeline in the ensemble."""
        return self.pipelines[index]

    def __iter__(self):
        """ Returns iterator over list of pipelines within the ensemble."""
        return iter(self.pipelines)

    @property
    def classes_(self):
        p = self.pipelines[0]
        if hasattr(p, 'classes_'):
            return p.classes_
        else:
            return NotImplementedError

    @property
    def feature_importances_(self):
        if self.classification:
            values = np.zeros(shape=(self._num_features,))
            cnt = 0
            for p in self.pipelines:
                if hasattr(p, 'feature_importances_'):
                    values += np.asarray(p.feature_importances_)
                    cnt += 1
            if cnt > 0:
                values /= cnt
            return values.tolist()
        else:
            return self.coef_

    @property
    def coef_(self):
        if self.classification:
            return self.feature_importances_
        else:
            values = []
            cnt = 0
            for p in self.pipelines:
                if hasattr(p, 'coef_'):
                    values.append(np.asarray(p.feature_importances_))
                    cnt += 1
            if cnt > 0:
                min_len = min([len(v) for v in values])
                accum = np.zeros(shape=(min_len,))
                for v in values:
                    accum += v[:min_len]
                values = accum.tolist()
            else:
                values = [1.0]    # fake constant to pass through if nothing found
            return values


class Ensemble(BaseEnsemble):
    def __init__(self, options, pipelines, weights=None, classification=False):
        super(Ensemble, self).__init__(
            options=options,
            pipelines=pipelines,
            classification=classification,
            params=dict(
                pipelines=pipelines,
                weights=weights,
                classification=classification
            )
        )
        self.weights = weights

        if weights is None:
            length = len(self.pipelines)
            self.weights = np.asarray([1 / float(length)] * length)

    def _assemble_predicts(self, predicts):
        for i in range(predicts.shape[0]):
            predicts[i, :] = predicts[i, :] * self.weights[i]

        return np.sum(predicts, axis=0)

    def predict(self, x):
        if self.classification:  # soft_labels
            predicts = self.predict_proba(x)
        else:
            predicts = self._assemble_predicts(self._predict(x))

        if self.classification:
            predicts = self.le.inverse_transform(np.argmax(predicts, axis=1))
        return predicts

    def predict_proba(self, x):
        return self._assemble_predicts(self._predict_proba(x))


class Voting(BaseEnsemble):
    """ Voting ensemble for classification based on Majority/Weighted rule.
    It uses pipelines, where the last estimator should be an classifier.

    Parameters
    ----------
    pipelines : list of pipelines for classification.

    voting : str, {'hard', 'soft'} (default='soft')
        If 'hard', uses predicted class labels for majority rule voting.
        Else if 'soft', predicts the class label based on the argmax of
        the sums of the predicted probabilities.

    weights : array-like, shape = [n_pipelines], optional (default=`None`)
        Sequence of weights (`float` or `int`) to weight the occurrences of
        predicted class labels (`hard` voting) or class probabilities
        before averaging (`soft` voting). Uses uniform weights if `None`.
    """
    def __init__(self, options, pipelines, weights=None, n_best=3, voting='soft'):
        super(Voting, self).__init__(
            options=options,
            pipelines=pipelines[:n_best],
            classification=True,
            params=dict(
                pipelines=pipelines,
                weights=weights,
                n_best=n_best,
                voting=voting
            )
        )
        self.voting = voting
        self.weights = weights

    def predict(self, x):
        """ Predict class labels for x.

        Parameters
        ----------
        x : {array-like, matrix}, shape = [n_samples, n_features].

        Returns
        ----------
        predictions : array-like, shape = [n_samples] -> predicted class labels.
        """
        # check_is_fitted(self, 'pipelines')

        if self.voting == 'soft':
            avg = self.predict_proba(x)
            predictions = np.argmax(avg, axis=1)

        else:  # 'hard' voting
            predictions = np.apply_along_axis(
                lambda lbl: np.argmax(np.bincount(lbl, weights=self.weights)),
                axis=0, arr=self._predict(x)
            )
        return self.le.inverse_transform(predictions)

    def predict_proba(self, x):
        return np.average(self._predict_proba(x), axis=0, weights=self.weights)


class Averaging(BaseEnsemble):
    """ Averaging ensemble for classification and regression tasks.

    Parameters
    ----------
    pipelines : list of pipelines for classification.

    classification : bool, (default=False)
        If True, uses predicted class probabilities for averaging within them.
        If False, uses averaging over raw predicted values.

    weights : array-like, shape = [n_pipelines], optional (default=`None`)
        Sequence of weights (`float` or `int`) to weight the class probabilities (for `classification`)
        or values (for `regression`) before averaging. Uses uniform weights if `None`.
    """
    def __init__(self, options, pipelines, weights=None, n_best=3, classification=False):
        super(Averaging, self).__init__(
            options=options,
            pipelines=pipelines[:n_best],
            classification=classification,
            params=dict(
                pipelines=pipelines,
                weights=weights,
                n_best=n_best,
                classification=classification
            )
        )
        self.weights = weights

    def predict(self, x):
        """ Predict class labels for x.

        Parameters
        ----------
        x : {array-like, matrix}, shape = [n_samples, n_features].

        Returns
        ----------
        predictions : array-like, shape = [n_samples] -> predicted class labels or values.
        """

        if self.classification:
            avg = self.predict_proba(x)
            predictions = self.le.inverse_transform(np.argmax(avg, axis=1))

        else:  # 'regression' task_type
            predictions = np.average(self._predict(x), axis=0, weights=self.weights)

        return predictions

    def predict_proba(self, x):
        return np.average(self._predict_proba(x), axis=0, weights=self.weights)
