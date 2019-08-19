# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the explanations that are returned from explaining models."""

import numpy as np
import uuid
import json
import pandas as pd

from azureml.explain.model.common.explanation_utils import _sort_values, _order_imp
from azureml.explain.model.common.constants import Dynamic, ExplainParams, ExplanationParams, History, \
    ExplainType, ModelTask
from azureml.explain.model.dataset.dataset_wrapper import DatasetWrapper
from shap.common import DenseData

from ..common.explanation_utils import _get_raw_feature_importances

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from ..common.chained_identity import ChainedIdentity


class BaseExplanation(ChainedIdentity):
    """The common explanation returned by explainers.

    :param method: The explanation method used to explain the model (e.g. SHAP, LIME).
    :type method: str
    :param model_task: The task of the original model i.e. classification or regression.
    :type model_task: str
    :param model_type: The type of the original model that was explained,
        e.g. sklearn.linear_model.LinearRegression.
    :type model_type: str
    :param explanation_id: The unique identifier for the explanation.
    :type explanation_id: str
    """

    def __init__(self, method, model_task, model_type=None, explanation_id=None, **kwargs):
        """Create the common base explanation.

        :param method: The explanation method used to explain the model (e.g. SHAP, LIME).
        :type method: str
        :param model_task: The task of the original model i.e. classification or regression.
        :type model_task: str
        :param model_type: The type of the original model that was explained,
            e.g. sklearn.linear_model.LinearRegression.
        :type model_type: str
        :param explanation_id: The unique identifier for the explanation.
        :type explanation_id: str
        """
        super(BaseExplanation, self).__init__(**kwargs)
        self._logger.debug('Initializing BaseExplanation')
        self._method = method
        self._model_task = model_task
        self._model_type = model_type
        self._id = explanation_id or str(uuid.uuid4())

    @property
    def method(self):
        """Get the explanation method.

        :return: The explanation method.
        :rtype: str
        """
        return self._method

    @property
    def model_type(self):
        """Get the type of the original model that was explained.

        :return: A class name or 'function', if that information is available.
        :rtype: str
        """
        return self._model_type

    @property
    def model_task(self):
        """Get the task of the original model, i.e. classification or regression (others possibly in the future).

        :return: The task of the original model.
        :rtype: str
        """
        return self._model_task

    @property
    def id(self):
        """Get the explanation id.

        :return: The explanation id.
        :rtype: str
        """
        return self._id

    @staticmethod
    def _does_quack(explanation):
        """Validate that the explanation object passed in is a valid BaseExplanation.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        if not hasattr(explanation, History.METHOD) or not isinstance(explanation.method, str):
            return False
        if not hasattr(explanation, History.ID) or not isinstance(explanation.id, str):
            return False
        if not hasattr(explanation, ExplainParams.MODEL_TASK) or not isinstance(explanation.model_task, str):
            return False
        if not hasattr(explanation, ExplainParams.MODEL_TYPE):
            return False
        return True


class FeatureImportanceExplanation(BaseExplanation):
    """The common feature importance explanation returned by explainers.

    :param features: The feature names.
    :type features: Union[list[str], list[int]]
    """

    def __init__(self, features=None, is_raw=False, **kwargs):
        """Create the feature importance explanation from the given feature names.

        :param features: The feature names.
        :type features: Union[list[str], list[int]]
        :param is_raw: Whether the explanation is on the original (raw) features or engineered ones.
        :type is_raw: bool
        """
        super(FeatureImportanceExplanation, self).__init__(**kwargs)
        self._logger.debug('Initializing FeatureImportanceExplanation')
        self._features = features
        self._is_raw = is_raw

    @property
    def features(self):
        """Get the feature names.

        :return: The feature names.
        :rtype: list[str]
        """
        if not isinstance(self._features, list) and self._features is not None:
            return self._features.tolist()
        return self._features

    @property
    def is_raw(self):
        """Get the raw explanation flag.

        :return: A boolean, True if it's a raw explanation.
        :rtype: bool
        """
        return self._is_raw

    @classmethod
    def _does_quack(cls, explanation):
        """Validate that the explanation object passed in is a valid BaseExplanation.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        if not super()._does_quack(explanation):
            return False
        if not hasattr(explanation, History.FEATURES):
            return False
        if not hasattr(explanation, ExplainType.IS_RAW) or not isinstance(explanation.is_raw, bool):
            return False
        return True


class LocalExplanation(FeatureImportanceExplanation):
    """The common local explanation returned by explainers.

    :param local_importance_values: The feature importance values.
    :type local_importance_values: numpy.array
    """

    def __init__(self, local_importance_values=None, **kwargs):
        """Create the local explanation from the explainer's feature importance values.

        :param local_importance_values: The feature importance values.
        :type local_importance_values: numpy.array
        """
        super(LocalExplanation, self).__init__(**kwargs)
        self._logger.debug('Initializing LocalExplanation')
        self._local_importance_values = local_importance_values

    @property
    def local_importance_values(self):
        """Get the feature importance values in original order.

        :return: For a model with a single output such as regression, this
            returns a list of feature importance values for each data point. For models with vector outputs this
            function returns a list of such lists, one for each output. The dimension of this matrix
            is (# examples x # features).
        :rtype: list[list[float]] or list[list[list[float]]]
        """
        return self._local_importance_values.tolist()

    def get_local_importance_rank(self):
        """Get local feature importance rank or indexes.

        For example, if original features are
        [f0, f1, f2, f3] and in local importance order for the first data point they are [f2, f3, f0, f1],
        local_importance_rank[0] would be [2, 3, 0, 1] (or local_importance_rank[0][0] if classification)

        :return: The feature indexes sorted by importance.
        :rtype: list[list[int]] or list[list[list[int]]]
        """
        return _order_imp(self._local_importance_values).tolist()

    def get_ranked_local_names(self, top_k=None):
        """Get feature names sorted by local feature importance values, highest to lowest.

        :param top_k: If specified, only the top k names will be returned.
        :type top_k: int
        :return: The list of sorted features unless feature names are unavailable, feature indexes otherwise.
        :rtype: list[list[int or str]] or list[list[list[int or str]]]
        """
        if self._features is not None:
            self._ranked_local_names = _sort_values(self._features, np.array(self.get_local_importance_rank()))
            ranked_local_names = self._ranked_local_names
        else:
            ranked_local_names = np.array(self.get_local_importance_rank())

        if top_k is not None:
            # Note: only slice at the last dimension for top_k
            # Classification is 3D array and regression is 2D, but we only want to select
            # top_k features on the last dimension
            ranked_local_names = ranked_local_names[..., :top_k]
        return ranked_local_names.tolist()

    def get_ranked_local_values(self, top_k=None):
        """Get local feature importance sorted from highest to lowest.

        :param top_k: If specified, only the top k values will be returned.
        :type top_k: int
        :return: The list of sorted values.
        :rtype: list[list[float]] or list[list[list[float]]]
        """
        if len(self._local_importance_values.shape) == 1:
            sorted_values = _sort_values(self._local_importance_values, np.array(self.get_local_importance_rank()))
            self._ranked_local_values = sorted_values
        elif len(self._local_importance_values.shape) == 2:
            # Regression case, 2D array
            row_indexes = [[i] for i in range(len(self._local_importance_values))]
            self._ranked_local_values = self._local_importance_values[row_indexes, self.get_local_importance_rank()]
        else:
            # Classification case, list of 2D array
            classes = [[[i]] for i in range(len(self._local_importance_values))]
            row_indexes = [[i] for i in range(len(self._local_importance_values[0]))]
            self._ranked_local_values = self._local_importance_values[classes, row_indexes,
                                                                      self.get_local_importance_rank()]
        if top_k is not None:
            # Note: only slice at the last dimension for top_k
            # Classification is 3D array and regression is 2D, but we only want to select
            # top_k features on the last dimension
            return self._ranked_local_values[..., :top_k].tolist()
        return self._ranked_local_values.tolist()

    def get_raw_feature_importances(self, raw_to_output_maps):
        """Get local raw feature importance.

        :param raw_to_output_feature_maps: list of feature maps from raw to generated feature.
        :type raw_to_output_feature_maps: list[numpy.array]
        :return: raw feature importances
        :rtype: list[list] or list[list[list]]
        """
        return _get_raw_feature_importances(np.array(self.local_importance_values), raw_to_output_maps).tolist()

    @classmethod
    def _does_quack(cls, explanation):
        """Validate that the explanation object passed in is a valid LocalExplanation.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        if not super()._does_quack(explanation):
            return False
        if not hasattr(explanation, History.LOCAL_IMPORTANCE_VALUES):
            return False
        if not isinstance(explanation.local_importance_values, list):
            return False
        return True


class GlobalExplanation(FeatureImportanceExplanation):
    """The common global explanation returned by explainers.

    :param global_importance_values: The feature importance values in the order of the original features.
    :type global_importance_values: numpy.array
    :param global_importance_rank: The feature indexes sorted by importance.
    :type global_importance_rank: numpy.array
    :param ranked_global_names: The feature names sorted by importance.
    :type ranked_global_names: list[str] TODO
    :param ranked_global_values: The feature importance values sorted by importance.
    :type ranked_global_values: numpy.array
    """

    def __init__(self,
                 global_importance_values=None,
                 global_importance_rank=None,
                 ranked_global_names=None,
                 ranked_global_values=None,
                 **kwargs):
        """Create the global explanation from the explainer's overall importance values and order.

        :param global_importance_values: The feature importance values in the order of the original features.
        :type global_importance_values: numpy.array
        :param global_importance_rank: The feature indexes sorted by importance.
        :type global_importance_rank: numpy.array
        :param ranked_global_names: The feature names sorted by importance.
        :type ranked_global_names: list[str] TODO
        :param ranked_global_values: The feature importance values sorted by importance.
        :type ranked_global_values: numpy.array
        """
        super(GlobalExplanation, self).__init__(**kwargs)
        self._logger.debug('Initializing GlobalExplanation')
        self._global_importance_values = global_importance_values
        self._global_importance_rank = global_importance_rank
        self._ranked_global_names = ranked_global_names
        self._ranked_global_values = ranked_global_values

    @property
    def global_importance_values(self):
        """Get the global feature importance values.

        Values will be in their original order, the same as features, unless top_k was passed into
        upload_model_explanation or download_model_explanation. In those cases, returns the most important k values
        in highest to lowest importance order.

        :return: The model level feature importance values.
        :rtype: list[float]
        """
        if self._global_importance_values is None:
            return self._ranked_global_values
        return self._global_importance_values.tolist()

    @property
    def global_importance_rank(self):
        """Get the overall feature importance rank or indexes.

        For example, if original features are
        [f0, f1, f2, f3] and in global importance order they are [f2, f3, f0, f1], global_importance_rank
        would be [2, 3, 0, 1].

        :return: The feature indexes sorted by importance.
        :rtype: list[int]
        """
        return self._global_importance_rank.tolist()

    def get_ranked_global_names(self, top_k=None):
        """Get feature names sorted by global feature importance values, highest to lowest.

        :param top_k: If specified, only the top k names will be returned.
        :type top_k: int
        :return: The list of sorted features unless feature names are unavailable, feature indexes otherwise.
        :rtype: list[str] or list[int]
        """
        if self._ranked_global_names is None and self._features is not None:
            self._ranked_global_names = _sort_values(self._features, self._global_importance_rank)

        if self._ranked_global_names is not None:
            ranked_global_names = self._ranked_global_names
        else:
            ranked_global_names = self._global_importance_rank

        if top_k is not None:
            return ranked_global_names[:top_k].tolist()
        return ranked_global_names.tolist()

    def get_ranked_global_values(self, top_k=None):
        """Get global feature importance sorted from highest to lowest.

        :param top_k: If specified, only the top k values will be returned.
        :type top_k: int
        :return: The list of sorted values.
        :rtype: list[float]
        """
        if self._ranked_global_values is None:
            self._ranked_global_values = _sort_values(self._global_importance_values,
                                                      self._global_importance_rank)
        if top_k is not None:
            return self._ranked_global_values[:top_k].tolist()
        return self._ranked_global_values.tolist()

    def get_raw_feature_importances(self, feature_maps):
        """Get global raw feature importance.

        :param raw_feat_indices: list of lists of generated feature indices for each raw feature
        :type raw_feat_indices: list[list]
        :param weights: list of list of weights to be applied to the generated feature importance
        :type weights: list[list]
        :return: raw feature importances
        :rtype: list[list] or list[list[list]]

        """
        return _get_raw_feature_importances(
            np.array(self.global_importance_values), feature_maps).tolist()

    def get_feature_importance_dict(self, top_k=None):
        """Get a dictionary pairing ranked global names and feature importance values.

        :param top_k: If specified, only the top k names and values will be returned.
        :type top_k: int
        :return: A dictionary of feature names and their importance values.
        :rtype: dict{str: float}
        """
        names = self.get_ranked_global_names(top_k=top_k)
        values = self.get_ranked_global_values(top_k=top_k)
        return dict(zip(names, values))

    @classmethod
    def _does_quack(cls, explanation):
        """Validate that the explanation object passed in is a valid GlobalExplanation.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        if not super()._does_quack(explanation):
            return False
        if not hasattr(explanation, History.GLOBAL_IMPORTANCE_VALUES) or explanation.global_importance_values is None:
            return False
        if not hasattr(explanation, History.GLOBAL_IMPORTANCE_RANK) or explanation.global_importance_rank is None:
            return False
        return True


class ExpectedValuesMixin(object):
    """The explanation mixin for expected values.

    :param expected_values: The expected values of the model.
    :type expected_values: np.array
    """

    def __init__(self, expected_values=None, **kwargs):
        """Create the expected values mixin and set the expected values.

        :param expected_values: The expected values of the model.
        :type expected_values: np.array
        """
        super(ExpectedValuesMixin, self).__init__(**kwargs)
        self._expected_values = expected_values

    @property
    def expected_values(self):
        """Get the expected values.

        :return: The expected value of the model applied to the set of initialization examples.
        :rtype: list
        """
        vals = self._expected_values
        if isinstance(self._expected_values, np.ndarray):
            vals = vals.tolist()
        if not isinstance(vals, list):
            vals = [vals]
        return vals

    @staticmethod
    def _does_quack(explanation):
        """Validate that the explanation object passed in is a valid ExpectedValuesMixin.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        if not hasattr(explanation, History.EXPECTED_VALUES) or explanation.expected_values is None:
            return False
        return True


class ClassesMixin(object):
    """The explanation mixin for classes.

    This mixin is added when the user specifies classes in the classification
    scenario when creating a global or local explanation.
    This is activated when the user specifies the classes parameter for global
    or local explanations.

    :param classes: Class names as a list of strings. The order of
        the class names should match that of the model output.
    :type classes: list[str]
    """

    def __init__(self, classes=None, **kwargs):
        """Create the classes mixin and set the classes.

        :param classes: Class names as a list of strings. The order of
            the class names should match that of the model output.
        :type classes: list[str]
        """
        super(ClassesMixin, self).__init__(**kwargs)
        self._classes = classes

    @property
    def classes(self):
        """Get the classes.

        :return: The list of classes.
        :rtype: list
        """
        return self._classes

    @staticmethod
    def _does_quack(explanation):
        """Validate that the explanation object passed in is a valid ClassesMixin.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        return hasattr(explanation, History.CLASSES)


class PerClassMixin(ClassesMixin):
    """The explanation mixin for per class aggregated information.

    This mixin is added for the classification scenario for global
    explanations.  The per class importance values are group averages of
    local importance values across different classes.

    :param per_class_values: The feature importance values for each class in the order of the original features.
    :type per_class_values: numpy.array
    :param per_class_importance_rank: The feature indexes for each class sorted by importance.
    :type per_class_importance_rank: numpy.array
    :param ranked_per_class_names: The feature names for each class sorted by importance.
    :type ranked_per_class_names: list[str]
    :param ranked_per_class_values: The feature importance values sorted by importance.
    :type ranked_per_class_values: numpy.array
    """

    def __init__(self,
                 per_class_values=None,
                 per_class_rank=None,
                 ranked_per_class_names=None,
                 ranked_per_class_values=None,
                 **kwargs):
        """Create the per class mixin from the explainer's importance values and order.

        :param per_class_values: The feature importance values for each class in the order of the original features.
        :type per_class_values: numpy.array
        :param per_class_importance_rank: The feature indexes for each class sorted by importance.
        :type per_class_importance_rank: numpy.array
        :param ranked_per_class_names: The feature names for each class sorted by importance.
        :type ranked_per_class_names: list[str]
        :param ranked_per_class_values: The feature importance values sorted by importance.
        :type ranked_per_class_values: numpy.array
        """
        super(PerClassMixin, self).__init__(**kwargs)
        self._per_class_values = per_class_values
        self._per_class_rank = per_class_rank
        self._ranked_per_class_names = ranked_per_class_names
        self._ranked_per_class_values = ranked_per_class_values

    @property
    def per_class_values(self):
        """Get the per class importance values.

        Values will be in their original order, the same as features, unless top_k was passed into
        upload_model_explanation or download_model_explanation. In those cases, returns the most important k values
        in highest to lowest importance order.

        :return: The model level per class feature importance values in original feature order.
        :rtype: list
        """
        if self._per_class_values is None:
            return self._ranked_per_class_values.tolist()
        return self._per_class_values.tolist()

    @property
    def per_class_rank(self):
        """Get the per class importance rank or indexes.

        For example, if original features are
        [f0, f1, f2, f3] and in per class importance order they are [[f2, f3, f0, f1], [f0, f2, f3, f1]],
        per_class_rank would be [[2, 3, 0, 1], [0, 2, 3, 1]].

        :return: The per class indexes that would sort per_class_values.
        :rtype: list
        """
        return self._per_class_rank.tolist()

    def get_ranked_per_class_names(self, top_k=None):
        """Get feature names sorted by per class feature importance values, highest to lowest.

        :param top_k: If specified, only the top k names will be returned.
        :type top_k: int
        :return: The list of sorted features unless feature names are unavailable, feature indexes otherwise.
        :rtype: list[list[str]] or list[list[int]]
        """
        if self._ranked_per_class_names is None and self._features is not None:
            self._ranked_per_class_names = _sort_values(self._features, self._per_class_rank)

        if self._ranked_per_class_names is not None:
            ranked_per_class_names = self._ranked_per_class_names
        else:
            ranked_per_class_names = self._per_class_rank

        if top_k is not None:
            ranked_per_class_names = ranked_per_class_names[:, :top_k]
        return ranked_per_class_names.tolist()

    def get_ranked_per_class_values(self, top_k=None):
        """Get per class feature importance sorted from highest to lowest.

        :param top_k: If specified, only the top k values will be returned.
        :type top_k: int
        :return: The list of sorted values.
        :rtype: list[list[float]]
        """
        if self._ranked_per_class_values is None:
            row_indexes = np.arange(len(self._per_class_values))[:, np.newaxis]
            self._ranked_per_class_values = self._per_class_values[row_indexes, self._per_class_rank]
        if top_k is not None:
            return self._ranked_per_class_values[:, :top_k].tolist()
        return self._ranked_per_class_values.tolist()

    @classmethod
    def _does_quack(cls, explanation):
        """Validate that the explanation object passed in is a valid PerClassMixin.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        if not super()._does_quack(explanation):
            return False
        if not hasattr(explanation, History.PER_CLASS_VALUES) or explanation.per_class_values is None:
            return False
        if not hasattr(explanation, History.PER_CLASS_RANK) or explanation.per_class_rank is None:
            return False
        return True


class _DatasetsMixin(object):
    """The dataset mixin for storing datasets or their reference IDs.

    If this explanation has been downloaded from run history, these will always be ID strings.

    :param init_data: The initialization (background) data used in the explanation, or a Dataset ID.
    :type init_data: np.array or str
    :param eval_data: The evaluation (testing) data used in the explanation, or a Dataset ID.
    :type eval_data: np.array or str
    """

    def __init__(self,
                 init_data=None,
                 eval_data=None,
                 **kwargs):
        """Create the dataset mixin for storing datasets or their reference IDs.

        If this explanation has been downloaded from run history, these will always be ID strings.

        :param init_data: The initialization (background) data used in the explanation, or a Dataset ID.
        :type init_data: np.array or str
        :param eval_data: The evaluation (testing) data used in the explanation, or a Dataset ID.
        :type eval_data: np.array or str
        """
        super(_DatasetsMixin, self).__init__(**kwargs)
        self._init_data = init_data
        self._eval_data = eval_data

    @property
    def init_data(self):
        """Get initialization (background) data or the Dataset ID.

        :return: The dataset or dataset ID.
        :rtype: list or str
        """
        return self._init_data

    @property
    def eval_data(self):
        """Get evaluation (testing) data or the Dataset ID.

        :return: The dataset or dataset ID.
        :rtype: list or str
        """
        return self._eval_data

    @staticmethod
    def _does_quack(explanation):
        """Validate that the explanation object passed in is a valid _DatasetsMixin.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        return hasattr(explanation, History.INIT_DATA) and hasattr(explanation, History.EVAL_DATA)


class _ModelIdMixin(object):
    """The model ID mixin for storing model IDs when they are available.

    :param model_id: The ID of an MMS model.
    :type model_id: str
    """

    def __init__(self, model_id=None, **kwargs):
        """Create the model ID mixin for storing model IDs when they are available.

        :param model_id: The ID of an MMS model.
        :type model_id: str
        """
        super(_ModelIdMixin, self).__init__(**kwargs)
        self._model_id = model_id

    @property
    def model_id(self):
        """Get the model ID.

        :return: The model ID.
        :rtype: str
        """
        return self._model_id

    @staticmethod
    def _does_quack(explanation):
        """Validate that the explanation object passed in is a valid _ModelIdMixin.

        :param explanation: The explanation to be validated.
        :type explanation: object
        :return: True if valid else False
        :rtype: bool
        """
        return hasattr(explanation, History.MODEL_ID)


def _create_local_explanation(expected_values=None, classification=True, explanation_id=None, init_data=None,
                              eval_data=None, model_id=None, **kwargs):
    """Dynamically creates an explanation based on local type and specified data.

    :param expected_values: The expected values of the model.
    :type expected_values: list
    :param classification: Indicates if this is a classification or regression explanation.
    :type classification: bool
    :param explanation_id: If specified, puts the local explanation under a preexisting explanation object.
        If not, a new unique identifier will be created for the explanation.
    :type explanation_id: str
    :param init_data: The initialization (background) data for the explanation.
    :type init_data: list
    :param eval_data: The evaluation (testing) data for the explanation.
    :type eval_data: list
    :param model_id: The model ID.
    :type model_id: str
    :return: A model explanation object. It is guaranteed to be a LocalExplanation. If expected_values is not None, it
        will also have the properties of the ExpectedValuesMixin. If classification is set to True, it will have the
        properties of the ClassesMixin.
    :rtype: DynamicLocalExplanation
    """
    exp_id = explanation_id or str(uuid.uuid4())
    mixins = [LocalExplanation]
    if expected_values is not None:
        mixins.append(ExpectedValuesMixin)
        kwargs[ExplanationParams.EXPECTED_VALUES] = expected_values
    if classification:
        mixins.append(ClassesMixin)
    if classification:
        kwargs[ExplainParams.MODEL_TASK] = ExplainType.CLASSIFICATION
    else:
        kwargs[ExplainParams.MODEL_TASK] = ExplainType.REGRESSION
    if init_data is not None or eval_data is not None:
        mixins.append(_DatasetsMixin)
        if init_data is not None:
            kwargs[History.INIT_DATA] = init_data
        if eval_data is not None:
            kwargs[History.EVAL_DATA] = eval_data
    if model_id is not None:
        mixins.append(_ModelIdMixin)
        kwargs[History.MODEL_ID] = model_id
    DynamicLocalExplanation = type(Dynamic.LOCAL_EXPLANATION, tuple(mixins), {})
    local_explanation = DynamicLocalExplanation(explanation_id=exp_id, **kwargs)
    return local_explanation


def _create_global_explanation_kwargs(local_explanation=None, expected_values=None, classification=True,
                                      explanation_id=None, init_data=None, eval_data=None, model_id=None, **kwargs):
    """Return the arguments for dynamically creating a global explanation.

    :param local_explanation: The local explanation information to include with global,
        can be done when the global explanation is a summary of local explanations.
    :type local_explanation: LocalExplanation
        :param expected_values: The expected values of the model.
        :type expected_values: list
    :param classification: Indicates if this is a classification or regression explanation.
    :type classification: bool
    :param explanation_id: If specified, puts the global explanation under a preexisting explanation object.
        If not, a new unique identifier will be created for the explanation.
    :type explanation_id: str
    :param init_data: The initialization (background) data for the explanation.
    :type init_data: list
    :param eval_data: The evaluation (testing) data for the explanation.
    :param eval_data: list
    :param model_id: The model ID.
    :type model_id: str
    :return: The kwargs and mixins for creating a DynamicGlobalExplanation.
    :rtype: (dict, list)
    """
    if local_explanation is not None:
        exp_id = local_explanation.id
    else:
        exp_id = explanation_id or str(uuid.uuid4())
    kwargs[ExplainParams.EXPLANATION_ID] = exp_id
    mixins = [GlobalExplanation]
    # Special case: for aggregate explanations, we can include both global
    # and local explanations for the user as an optimization, so they
    # don't have to call both explain_global and explain_local and redo the
    # same computation twice
    if local_explanation is not None:
        mixins.append(LocalExplanation)
        kwargs[ExplainParams.LOCAL_IMPORTANCE_VALUES] = local_explanation._local_importance_values
    # In the mimic case, we don't aggregate so we can't have per class information
    # but currently in other cases when we aggregate local explanations we get per class
    if classification:
        if local_explanation is not None or ExplainParams.PER_CLASS_VALUES in kwargs:
            mixins.append(PerClassMixin)
        else:
            mixins.append(ClassesMixin)
    if expected_values is not None:
        mixins.append(ExpectedValuesMixin)
        kwargs[ExplanationParams.EXPECTED_VALUES] = expected_values
    if classification:
        kwargs[ExplainParams.MODEL_TASK] = ExplainType.CLASSIFICATION
    else:
        kwargs[ExplainParams.MODEL_TASK] = ExplainType.REGRESSION
    if init_data is not None or eval_data is not None:
        mixins.append(_DatasetsMixin)
        if init_data is not None:
            kwargs[History.INIT_DATA] = init_data
        if eval_data is not None:
            kwargs[History.EVAL_DATA] = eval_data
    if model_id is not None:
        mixins.append(_ModelIdMixin)
        kwargs[History.MODEL_ID] = model_id
    return kwargs, mixins


def _create_global_explanation(local_explanation=None, expected_values=None,
                               classification=True, explanation_id=None, **kwargs):
    """Dynamically creates an explanation based on global type and specified data.

    :param local_explanation: The local explanation information to include with global,
        can be done when the global explanation is a summary of local explanations.
    :type local_explanation: LocalExplanation
        :param expected_values: The expected values of the model.
        :type expected_values: list
    :param classification: Indicates if this is a classification or regression explanation.
    :type classification: bool
    :param explanation_id: If specified, puts the global explanation under a preexisting explanation object.
        If not, a new unique identifier will be created for the explanation.
    :type explanation_id: str
    :return: A model explanation object. It is guaranteed to be a GlobalExplanation. If local_explanation is not None,
        it will also have the properties of a LocalExplanation. If expected_values is not None, it will have the
        properties of ExpectedValuesMixin. If classification is set to True, it will have the properties of
        ClassesMixin, and if a local explanation was passed in it will also have the properties of PerClassMixin.
    :rtype: DynamicGlobalExplanation
    """
    kwargs, mixins = _create_global_explanation_kwargs(local_explanation, expected_values,
                                                       classification, explanation_id, **kwargs)
    DynamicGlobalExplanation = type(Dynamic.GLOBAL_EXPLANATION, tuple(mixins), {})
    global_explanation = DynamicGlobalExplanation(**kwargs)
    return global_explanation


def _get_aggregate_kwargs(local_explanation=None, include_local=True,
                          features=None, explanation_id=None, **kwargs):
    """Aggregate the local explanation and return the arguments for creating a global explanation.

    :param local_explanation: The local explanation to summarize.
    :type local_explanation: LocalExplanation
    :param include_local: Whether the global explanation should also include local information.
    :type include_local: bool
    :param features: A list of feature names.
    :type features: list[str]
    :param explanation_id: If specified, puts the aggregated explanation under a preexisting explanation object.
        If not, a new unique identifier will be created for the explanation.
    :type explanation_id: str
    :return: The arguments for creating a global explanation.
    :rtype: dict
    """
    if local_explanation is not None:
        exp_id = local_explanation.id
    else:
        exp_id = explanation_id or str(uuid.uuid4())
    features = local_explanation.features
    kwargs[ExplainParams.FEATURES] = features
    kwargs[ExplainParams.IS_RAW] = local_explanation.is_raw
    local_importance_values = local_explanation._local_importance_values
    classification = ClassesMixin._does_quack(local_explanation)
    if classification:
        per_class_values = np.mean(np.absolute(local_importance_values), axis=1)
        per_class_rank = _order_imp(per_class_values)
        global_importance_values = np.mean(per_class_values, axis=0)
        global_importance_rank = _order_imp(global_importance_values)
        kwargs[ExplainParams.PER_CLASS_VALUES] = per_class_values
        kwargs[ExplainParams.PER_CLASS_RANK] = per_class_rank
    else:
        global_importance_values = np.mean(np.absolute(local_importance_values), axis=0)
        global_importance_rank = _order_imp(global_importance_values)

    kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK] = global_importance_rank
    kwargs[ExplainParams.GLOBAL_IMPORTANCE_VALUES] = global_importance_values
    expected_values = None
    if ExpectedValuesMixin._does_quack(local_explanation):
        expected_values = np.array(local_explanation.expected_values)
    if include_local:
        kwargs[ExplainParams.LOCAL_EXPLANATION] = local_explanation
    kwargs[ExplainParams.EXPECTED_VALUES] = expected_values
    kwargs[ExplainParams.EXPLANATION_ID] = exp_id
    kwargs[ExplainParams.CLASSIFICATION] = classification
    return kwargs


def _aggregate_global_from_local_explanation(local_explanation=None, include_local=True,
                                             features=None, explanation_id=None, **kwargs):
    """Aggregate the local explanation information to global through averaging.

    :param local_explanation: The local explanation to summarize.
    :type local_explanation: LocalExplanation
    :param include_local: Whether the global explanation should also include local information.
    :type include_local: bool
    :param features: A list of feature names.
    :type features: list[str]
    :param explanation_id: If specified, puts the aggregated explanation under a preexisting explanation object.
        If not, a new unique identifier will be created for the explanation.
    :type explanation_id: str
    :return: A model explanation object. It is guaranteed to be a GlobalExplanation. If include_local is set to True,
        it will also have the properties of a LocalExplanation. If expected_values exists on local_explanation, it
        will have the properties of ExpectedValuesMixin. If local_explanation has ClassesMixin, it will have the
        properties of PerClassMixin.
    :rtype: DynamicGlobalExplanation
    """
    kwargs = _get_aggregate_kwargs(local_explanation, include_local, features, explanation_id, **kwargs)
    return _create_global_explanation(**kwargs)


def _create_raw_feats_global_explanation(engineered_feats_explanation, feature_map=None, **kwargs):
    raw_importances = engineered_feats_explanation.get_raw_feature_importances([feature_map])
    order = _order_imp(np.array(raw_importances))
    new_kwargs = kwargs.copy()
    new_kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK] = order

    if hasattr(engineered_feats_explanation, ExplainParams.LOCAL_IMPORTANCE_VALUES):
        local_explanation = LocalExplanation(np.array(engineered_feats_explanation.local_importance_values),
                                             model_task=kwargs[ExplainParams.MODEL_TASK], method=None, features=None)
        raw_local_importances = local_explanation.get_raw_feature_importances([feature_map])
        raw_local_explanation = LocalExplanation(
            np.array(raw_local_importances),
            model_task=kwargs.get(ExplainParams.MODEL_TASK, None),
            method=kwargs.get(ExplainParams.METHOD, None),
            features=kwargs.get(ExplainParams.FEATURES, None))
        new_kwargs[ExplainParams.LOCAL_EXPLANATION] = raw_local_explanation
        if hasattr(engineered_feats_explanation, ExplainParams.PER_CLASS_VALUES):
            per_class_values = np.mean(np.absolute(raw_local_importances), axis=1)
            per_class_rank = _order_imp(np.array(per_class_values))
            new_kwargs[ExplainParams.PER_CLASS_VALUES] = per_class_values
            new_kwargs[ExplainParams.PER_CLASS_RANK] = per_class_rank

    return _create_global_explanation(global_importance_values=np.array(raw_importances), **new_kwargs)


def _create_raw_feats_local_explanation(engineered_feats_explanation, feature_map=None, **kwargs):
    raw_importances = engineered_feats_explanation.get_raw_feature_importances([feature_map])
    return _create_local_explanation(local_importance_values=np.array(raw_importances), **kwargs)


def _aggregate_streamed_local_explanations(explainer, evaluation_examples, classification, features,
                                           batch_size, **kwargs):
    """Aggregate the local explanations via streaming fashion to global.

    :param explainer: The explainer used to create local explanations.
    :type explainer: BaseExplainer
    :param evaluation_examples: The evaluation examples.
    :type evaluation_examples: DatasetWrapper
    :param classification: Indicates if this is a classification or regression explanation.
        Unknown by default.
    :type classification: ModelTask
    :param features: The feature names.
    :type features: list
    :param batch_size: If include_local is True, specifies the batch size for aggregating
        local explanations to global.
    :type batch_size: int
    :return: kwargs to create a global explanation
    :rtype dict
    """
    if batch_size <= 0:
        raise ValueError("Specified argument batch_size must be greater than 0")
    importance_values = None
    expected_values = None
    dataset_len = evaluation_examples.dataset.shape[0]
    for i in range(0, dataset_len, batch_size):
        rows = evaluation_examples.dataset[i:i + batch_size]
        local_explanation_row = explainer.explain_local(rows)
        local_importance_values = np.abs(local_explanation_row._local_importance_values)[..., :rows.shape[0], :]
        reduction_axis = len(local_importance_values.shape) - 2
        if importance_values is None:
            importance_values = np.sum(local_importance_values, axis=reduction_axis)
            expected_values = local_explanation_row.expected_values
            if classification is ModelTask.Unknown and ClassesMixin._does_quack(local_explanation_row):
                classification = ModelTask.Classification
        else:
            # Compute sum of feature importance values
            # NOTE: if we ever overflow here we can use the streaming approach instead
            # Formula: avg_{n+1} = (avg_{n} * n + x_{n+1}) / (n + 1)
            # Code: importance_values = (importance_values * n + local_importance_values) / (n + 1)
            importance_values = importance_values + np.sum(local_importance_values, axis=reduction_axis)
    importance_values = importance_values / evaluation_examples.dataset.shape[0]
    classification = classification is ModelTask.Classification
    if classification:
        global_importance_values = np.mean(importance_values, axis=0)
        per_class_rank = _order_imp(importance_values)
        kwargs[ExplainParams.PER_CLASS_VALUES] = importance_values
        kwargs[ExplainParams.PER_CLASS_RANK] = per_class_rank
    else:
        global_importance_values = importance_values
    kwargs[ExplainParams.EXPECTED_VALUES] = np.array(expected_values)
    kwargs[ExplainParams.CLASSIFICATION] = classification
    kwargs[ExplainParams.GLOBAL_IMPORTANCE_VALUES] = global_importance_values
    kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK] = _order_imp(global_importance_values)
    kwargs[ExplainParams.FEATURES] = features
    return kwargs


def _get_raw_explainer_create_explanation_kwargs(*, kwargs=None, explanation=None):
    """Get kwargs for create explanation methods.

    :param kwargs: dictionary of key value pairs for create_local and create_global explanations
    :type kwargs: {str: str}
    :param explanation: explanation object
    :type explanation: DynamicGlobalExplanation or DynamicLocalExplanation
    :return: dictionary of arguments for _create_raw_feats_global_explanation and _create_raw_feats_local_explanation
     methods
    :rtype: {}
    """
    if explanation is not None and kwargs is not None:
        raise ValueError("Both explanation and kwargs cannot be set")

    keys = [ExplainParams.METHOD, ExplainParams.FEATURES, ExplainParams.CLASSES, ExplainParams.MODEL_TASK,
            ExplainParams.CLASSIFICATION]

    def has_value(x):
        if explanation is None:
            return x in kwargs
        else:
            return hasattr(explanation, x)

    def get_value(x):
        if explanation is None:
            return kwargs[x]
        else:
            return getattr(explanation, x)

    kwarg_dict = dict([(key, get_value(key)) for key in keys if has_value(key)])
    kwarg_dict[ExplainParams.IS_RAW] = True
    return kwarg_dict


def _transform_value_for_load(paramkey, expldict, _metadata):
    param = getattr(ExplainParams, paramkey)
    if paramkey != 'CLASSIFICATION':
        if param not in expldict:
            return None
        value = expldict[param]

    # special handling for classification
    if paramkey == 'CLASSIFICATION':
        model_task_param = getattr(ExplainParams, 'MODEL_TASK')
        model_task_value = expldict[model_task_param]
        if model_task_value is None or model_task_value == getattr(ExplainParams, 'CLASSIFICATION'):
            return True
        else:
            return False

    # assumes that all lists should be converted to np.array
    # unless otherwise indicated in _metadata
    if isinstance(value, list) and param not in _metadata:
        return np.array(value)

    if param in _metadata:
        if _metadata[param] == 'ndarray':
            return np.array(value)
        if _metadata[param] == 'DataFrame':
            return pd.DataFrame(value)
        if _metadata[param] == 'DatasetWrapper':
            return DatasetWrapper(value)
        if _metadata[param] == 'DenseData':
            return DatasetWrapper(value)

    # default - no tranformation needed
    return value


def save_explanation(explanation):
    """Serialize the explanation.

    :param explanation: the Explanation to be serialized
    :type explanation: Explanation
    :return: JSON-formatted explanation data
    :rtype: str
    """
    paramkeys = list(ExplainParams.get_serializable())
    expldict = dict()
    _metadata = dict()
    for paramkey in paramkeys:
        param = getattr(ExplainParams, paramkey)
        if hasattr(explanation, param):
            value = getattr(explanation, param)
            if isinstance(value, pd.DataFrame):
                expldict[param] = value.values.tolist()
                _metadata[param] = 'DataFrame'
            elif isinstance(value, DatasetWrapper):
                expldict[param] = value.original_dataset.tolist()
                _metadata[param] = 'DatasetWrapper'
            elif isinstance(value, DenseData):
                expldict[param] = value.original_dataset.tolist()
                _metadata[param] = 'DenseData'
            elif isinstance(value, np.ndarray):
                expldict[param] = value.tolist()
                _metadata[param] = 'ndarray'
            else:
                expldict[param] = value
    return json.dumps({
        '_metadata': _metadata,
        'explanation': expldict
    })


def load_explanation(expljson):
    """De-serialize the explanation.

    :param expljson: JSON-formatted explanation data
    :type expljson: str
    :return: the original Explanation
    :rtype: Explanation
    """
    expl = json.loads(expljson)
    expldict = expl['explanation']
    _metadata = expl['_metadata']

    # special handling for id & explanation_id
    paramkeys = list(ExplainParams.get_serializable() - set(['ID']))
    id_param = getattr(ExplainParams, 'ID')
    if id_param in expldict:
        id_value = expldict[id_param]
    else:
        id_value = None

    # params that are already passed as named constructor arguments should not go into kwargs
    for remove_key in ['INIT_DATA', 'EXPECTED_VALUES', 'CLASSIFICATION']:
        if getattr(ExplainParams, remove_key) in expldict:
            paramkeys.remove(remove_key)

    if expldict.get(ExplainParams.LOCAL_IMPORTANCE_VALUES, None) is not None:
        # Includes a local explanation
        local_kwargs = dict()
        omit_global_keys = ['GLOBAL_IMPORTANCE_NAMES', 'GLOBAL_IMPORTANCE_VALUES',
                            'GLOBAL_IMPORTANCE_RANK', 'PER_CLASS_RANK', 'PER_CLASS_VALUES']
        for paramkey in list(set(paramkeys) - set(omit_global_keys)):
            param = getattr(ExplainParams, paramkey)
            if param in expldict:
                local_kwargs[param] = _transform_value_for_load(paramkey, expldict, _metadata)
        local_explanation = _create_local_explanation(
            explanation_id=id_value,
            init_data=_transform_value_for_load('INIT_DATA', expldict, _metadata),
            classification=_transform_value_for_load('CLASSIFICATION', expldict, _metadata),
            expected_values=_transform_value_for_load('EXPECTED_VALUES', expldict, _metadata),
            **local_kwargs)
        if expldict.get(ExplainParams.GLOBAL_IMPORTANCE_VALUES, None) is not None:
            # BOTH Local and Global explanation
            global_kwargs = dict()
            if getattr(ExplainParams, 'LOCAL_EXPLANATION') in expldict:
                paramkeys.remove('LOCAL_EXPLANATION')
            for paramkey in paramkeys:
                param = getattr(ExplainParams, paramkey)
                if param in expldict:
                    global_kwargs[param] = _transform_value_for_load(paramkey, expldict, _metadata)
            return _create_global_explanation(
                explanation_id=id_value,
                init_data=_transform_value_for_load('INIT_DATA', expldict, _metadata),
                classification=_transform_value_for_load('CLASSIFICATION', expldict, _metadata),
                expected_values=_transform_value_for_load('EXPECTED_VALUES', expldict, _metadata),
                local_explanation=local_explanation,
                **global_kwargs)
        else:
            # Local explanation ONLY
            return local_explanation
    else:
        # Global explanation ONLY
        global_kwargs = dict()
        for paramkey in paramkeys:
            param = getattr(ExplainParams, paramkey)
            if param in expldict:
                global_kwargs[param] = _transform_value_for_load(paramkey, expldict, _metadata)
        return _create_global_explanation(
            explanation_id=id_value,
            init_data=_transform_value_for_load('INIT_DATA', expldict, _metadata),
            classification=_transform_value_for_load('CLASSIFICATION', expldict, _metadata),
            expected_values=_transform_value_for_load('EXPECTED_VALUES', expldict, _metadata),
            **global_kwargs)
