# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Objects that can be instantiated into model objects.

Used for generic serialization and deserialization for models,
which can be used for communication purposes.
"""

from typing import Any, Dict, List, Optional, Type, Union
import copy
import importlib
import inspect
import json
import pickle

import numpy as np
from sklearn import linear_model, pipeline, preprocessing

from automl.client.core.common import constants, model_wrappers, tf_wrappers
from automl.client.core.common.problem_info import ProblemInfo

try:
    import nimbusml as nml
    nimbusml_present = True
    from automl.client.core.common.nimbus_wrappers import (
        AveragedPerceptronBinaryClassifier, AveragedPerceptronMulticlassClassifier,
        NimbusMlClassifierMixin, NimbusMlRegressorMixin
    )
except ImportError:
    nimbusml_present = False

PREPROC_NAME = 'preproc'
SKLEARN_NAME = 'sklearn'
TF_NAME = 'tf'
YTRANS_NAME = 'y_transformer'
ENSEMBLE_NAME = 'ensemble'
SDK_ENSEMBLE_NAME = "sdk_ensemble"
NIMBUSML_NAME = 'nimbusml'
TIMESERIES_NAME = 'timeseries'
SK_PIPELINE_TYPE = SKLEARN_NAME
NIMBUSML_PIPELINE_TYPE = NIMBUSML_NAME

WRAPPERS_MODULE = 'automl.client.core.common.model_wrappers'
SK_PIPELINE_MODULE = "sklearn.pipeline"
SK_PIPELINE_CLASS_NAME = "Pipeline"
NIMBUSML_PIPELINE_MODULE = "nimbusml.pipeline"
NIMBUSML_PIPELINE_CLASS_NAME = "Pipeline"


class ObjectSpec:
    """Metaobject for serialization and deserialization."""

    def __init__(self, spec_class, module, class_name,
                 *param_args, **param_kwargs):
        """Create an ObjectSpec."""
        self.spec_class = spec_class
        self.module = module
        self.class_name = class_name
        self.param_args = param_args
        self.param_kwargs = param_kwargs
        self.prepared_kwargs = {}   # type: Dict[str, Any]

    @classmethod
    def from_dict(cls: Type['ObjectSpec'], d: Dict[str, Any]) -> 'ObjectSpec':
        """Deserialize an ObjectSpec from a dictionary.

        :param cls: the class of the object to create
        :param d: the dictionary to deserialize
        :return: ObjectSpec for the dictionary
        """
        ret = cls.__new__(cls)  # type: ObjectSpec
        ret.__dict__ = copy.deepcopy(d)
        return ret

    def to_dict(self):
        """Serialize an ObjectSpec to a dictionary.

        :return: the dictionary of ObjectSpec attributes
        """
        self.prepared_kwargs = {}
        d = copy.deepcopy(self.__dict__)
        return d

    def supports_constrained_fit(self):
        """
        Check if ObjectSpec supports constrained fit.

        Returns whether the pipeline step can stop given a time constraint
        Returns false for the ObjectSpec parent class
        """
        return False

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        raise NotImplementedError()

    def instantiate(self, problem_info, random_state=None, num_threads=1):
        """Create a new object with additional parameters.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :return: a new object from the module and class from the constructor
        """
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.class_name)

        self.prepare_kwargs(cls, problem_info, random_state=random_state,
                            num_threads=num_threads)

        return cls(*self.param_args, **self.prepared_kwargs)


class PreprocessorObject(ObjectSpec):
    """Serializable pipeline preprocessing step."""

    def __init__(self, *args, **kwargs):
        """Create a PreprocessorObject."""
        super(PreprocessorObject, self).__init__(
            PREPROC_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1):
        """Save parameters to be serialized.

        :param problem_info:
        :param random_state:
        :param num_threads:
        """
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)


class SklearnObject(ObjectSpec):
    """Serializable pipeline model step."""

    def __init__(self, *args, **kwargs):
        """Create a SklearnObject."""
        super(SklearnObject, self).__init__(SKLEARN_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        argspec = inspect.getfullargspec(cls)
        if argspec.args:
            if 'random_state' in argspec.args:
                self.prepared_kwargs['random_state'] = random_state

            if 'n_jobs' in argspec.args:
                self.prepared_kwargs['n_jobs'] = num_threads

            if 'problem_info' in argspec.args:
                self.prepared_kwargs['problem_info'] = problem_info


class NimbusMLObject(ObjectSpec):
    """Serializable NimbusML pipeline model step."""

    def __init__(self, *args, **kwargs):
        """Create a NimbusMLObject."""
        super(NimbusMLObject, self).__init__(NIMBUSML_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info, random_state, **kwargs):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)

        if issubclass(cls, NimbusMlClassifierMixin) or issubclass(cls, NimbusMlRegressorMixin):
            if problem_info.feature_column_names is not None and problem_info.label_column_name is not None:
                self.prepared_kwargs['feature'] = problem_info.feature_column_names
                self.prepared_kwargs['label'] = problem_info.label_column_name
            if problem_info.use_incremental_learning:
                self.prepared_kwargs['caching'] = 'None'

        if (issubclass(cls, AveragedPerceptronBinaryClassifier) or
                issubclass(cls, AveragedPerceptronMulticlassClassifier)):
            # map legacy hyperparameter names (from an old version of nimbusml) to updated hyperparameter names
            # (in newest version of nimbusml)
            hyperparam_names_old_to_new = {
                'init_wts_diameter': 'initial_weights_diameter',
                'l2_regularizer_weight': 'l2_regularization',
                'num_iterations': 'number_of_iterations'
            }
            for old_name, new_name in hyperparam_names_old_to_new.items():
                if old_name in self.prepared_kwargs:
                    self.prepared_kwargs[new_name] = self.prepared_kwargs.pop(old_name)

    def instantiate(self, problem_info, random_state=None, num_threads=1):
        """Create a new object with additional parameters.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :return: a new object from the module and class from the constructor
        """
        return super().instantiate(problem_info, random_state=random_state)


class TFObject(ObjectSpec):
    """TF Object."""

    def __init__(self, *args, **kwargs):
        """Create a TFOBject."""
        super(TFObject, self).__init__(TF_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)

        if random_state is not None:
            self.prepared_kwargs['seed'] = random_state

        if 'optimizer' in self.prepared_kwargs:
            opt_name = self.prepared_kwargs.pop('optimizer')
            if opt_name not in tf_wrappers.OPTIMIZERS:
                raise ValueError('Optimizer {0} not known.'.format(opt_name))

            if 'learning_rate' not in self.prepared_kwargs:
                raise ValueError('Optimizer requires learning rate.')

            if opt_name == 'momentum':
                opt = tf_wrappers.OPTIMIZERS[opt_name](
                    self.prepared_kwargs.pop('learning_rate'),
                    self.prepared_kwargs['momentum'])
            else:
                opt = tf_wrappers.OPTIMIZERS[opt_name](
                    self.prepared_kwargs.pop('learning_rate'))
            self.prepared_kwargs['optimizer'] = opt

            if 'momentum' in self.prepared_kwargs:
                self.prepared_kwargs.pop('momentum')

        self.prepared_kwargs['max_time'] = problem_info.get_time_constraint()

        if 'activation_fn' in self.prepared_kwargs:
            if (self.prepared_kwargs['activation_fn'] not in
                    tf_wrappers.ACTIVATION_FNS):
                raise ValueError('Unknown activation fn: {0}'.format(
                    self.prepared_kwargs['activation_fn']))
            self.prepared_kwargs['activation_fn'] = tf_wrappers.ACTIVATION_FNS[
                self.prepared_kwargs['activation_fn']]
        if problem_info.task == constants.Tasks.CLASSIFICATION:
            self.prepared_kwargs['n_classes'] = problem_info.dataset_classes

    def supports_constrained_fit(self):
        """Check if model supposrts constrained fit."""
        return True


class EnsembleObject(ObjectSpec):
    """The Ensemble Object."""

    MODEL_KEY = 'models'
    CLF_KEY = 'clf'
    WEIGHTS_KEY = 'weights'
    LGBM_KEY = 'lgbm'
    LGBM_FILE = '/tmp/lgbm.pkl'

    def __init__(self, task=constants.Tasks.CLASSIFICATION, **kwargs):
        """Create and ensemble object."""
        self.task = task
        super(EnsembleObject, self).__init__(
            ENSEMBLE_NAME, WRAPPERS_MODULE, 'EnsembleWrapper', **kwargs)

    @staticmethod
    def model_to_json(model):
        """Convert a model object to JSON."""
        # TODO refactor ensembles
        data = {}
        data['init_params'] = model.get_params()
        data['model_params'] = mp = {}
        for p in [key for key in model.__dict__ if (
                key[-1] == '_' and
                'path' not in key and
                key not in ['Cs_', 'alphas_', 'scores_'])]:
            try:
                mp[p] = getattr(model, p).tolist()
            except Exception:
                mp[p] = getattr(model, p)
        return json.dumps(data)

    @staticmethod
    def elastic_net_from_json(jstring):
        """Create a elasticnet regresion object from JSON."""
        data = json.loads(jstring)
        model = linear_model.ElasticNetCV(**data['init_params'])
        for name, p in data['model_params'].items():
            setattr(model, name, np.array(p))
        return model

    @staticmethod
    def logistic_regression_from_json(jstring):
        """Create a logistic regression object from JSON."""
        data = json.loads(jstring)
        model = linear_model.LogisticRegressionCV(**data['init_params'])
        for name, p in data['model_params'].items():
            setattr(model, name, np.array(p))
        return model

    @staticmethod
    def _lgbm_to_tmp(model):
        with open(EnsembleObject.LGBM_FILE, 'wb') as f:
            pickle.dump(model, f)
        return EnsembleObject.LGBM_KEY

    @staticmethod
    def _lgbm_from_tmp():
        with open(EnsembleObject.LGBM_FILE, 'rb') as f:
            model = pickle.load(f)
        return model

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        # Turn object dicts into specs so they get passed to wrapper
        # as instantiated objects.
        self.prepared_kwargs[EnsembleObject.MODEL_KEY] = [
            PipelineSpec.from_dict(
                obj_dict).instantiate_pipeline_spec(
                    problem_info, random_state=random_state)
            for obj_dict in self.param_kwargs[EnsembleObject.MODEL_KEY]]
        if EnsembleObject.CLF_KEY in self.prepared_kwargs:
            if (self.prepared_kwargs[EnsembleObject.CLF_KEY
                                     ] != EnsembleObject.LGBM_KEY):
                if self.task == constants.Tasks.CLASSIFICATION:
                    self.prepared_kwargs[EnsembleObject.CLF_KEY] = (
                        EnsembleObject.logistic_regression_from_json(
                            self.prepared_kwargs[EnsembleObject.CLF_KEY]))
                elif self.task == constants.Tasks.REGRESSION:
                    self.prepared_kwargs[EnsembleObject.CLF_KEY] = (
                        EnsembleObject.elastic_net_from_json(
                            self.prepared_kwargs[EnsembleObject.CLF_KEY]))
            else:
                self.prepared_kwargs[EnsembleObject.CLF_KEY] = (
                    EnsembleObject._lgbm_from_tmp())

    def instantiate(self, problem_info, random_state=None, num_threads=1):
        """Create a new object with additional parameters.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :return: a new object from the module and class from the constructor
        """
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.class_name)

        self.prepare_kwargs(cls, problem_info, random_state=random_state,
                            num_threads=num_threads)

        # only difference between this and inherited function is that this includes task
        return cls(*self.param_args, task=self.task, **self.prepared_kwargs)


class SdkEnsembleObject(ObjectSpec):
    """The object spec representing an Ensemble created through the SDK."""

    def __init__(self, *args, **kwargs):
        """Create an ensemble object for using it through AutoML SDK."""
        super(SdkEnsembleObject, self).__init__(
            SDK_ENSEMBLE_NAME,
            *args,
            **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        argspec = inspect.getfullargspec(cls)
        if argspec.args:
            if 'random_state' in argspec.args:
                self.prepared_kwargs['random_state'] = random_state

            if 'n_jobs' in argspec.args:
                self.prepared_kwargs['n_jobs'] = num_threads


class TimeseriesObject(ObjectSpec):
    """Pipeline object for timeseries."""

    def __init__(self, *args, **kwargs):
        """Create a TimeseriesObject object."""
        super(TimeseriesObject, self).__init__(
            TIMESERIES_NAME,
            *args,
            **kwargs)

    def prepare_kwargs(self, cls, problem_info, random_state=None, num_threads=1):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        self.prepared_kwargs[constants.TimeSeriesInternal.TIMESERIES_PARAM_DICT] = problem_info.timeseries_param_dict


class PipelineSpec:
    """Serializable pipeline."""

    CLASS_MAP = {
        PREPROC_NAME: PreprocessorObject,
        SKLEARN_NAME: SklearnObject,
        TF_NAME: TFObject,
        YTRANS_NAME: PreprocessorObject,
        ENSEMBLE_NAME: EnsembleObject,
        SDK_ENSEMBLE_NAME: SdkEnsembleObject,
        NIMBUSML_NAME: NimbusMLObject,
        TIMESERIES_NAME: TimeseriesObject
    }   # type: Dict[str, Type[ObjectSpec]]

    def __init__(self, objects, pid, module=SK_PIPELINE_MODULE, class_name=SK_PIPELINE_CLASS_NAME):
        """Create a PipelineSpec.

        :param objects: a list of ObjectSpecs
        :param pid: the pipeline ID
        :param type: the type of Pipeline (SKLearn or Nimbus or something else.)
        """
        self.objects = objects
        self.pipeline_id = pid
        self.module = module
        self.class_name = class_name

    @staticmethod
    def from_dict(d):
        """Deserializes a PipelineSpec from a dictionary.

        :param d: the dictionary to deserialize
        :return: the PipelineSpec created from d
        """
        objs = [PipelineSpec.CLASS_MAP[o['spec_class']].from_dict(o)
                for o in d['objects']]
        module = d.get('module', SK_PIPELINE_MODULE)
        class_name = d.get('class_name', SK_PIPELINE_CLASS_NAME)
        ret = PipelineSpec(objs, d['pipeline_id'], module=module, class_name=class_name)

        return ret

    def to_dict(self):
        """Serialize a PipelineSpec to a dictionary.

        :return: the dictionary containing the steps of the pipeline serialized
            as dictionaries
        """
        d = copy.deepcopy(self.__dict__)
        d['objects'] = [o.to_dict() for o in self.objects]
        return d

    def class_strings(self):
        """Return a list of class names for each step in the pipeline."""
        return [o.class_name for o in self.objects]

    def summary(self):
        """Return a string representation of the pipeline (via class names)."""
        return '{ ' + ', '.join(self.class_strings()) + ' }'

    def supports_constrained_fit(self):
        """Indicate if the model can stop itself according to time constriant.

        Currently implemented as an any(), which is just a
        concise way to find the model object.
        """
        return any([o.supports_constrained_fit() for o in self.objects])

    def instantiate_pipeline_spec(self,
                                  problem_info: ProblemInfo,
                                  random_state: Optional[int] = None,
                                  is_sparse: bool = False) -> Union[pipeline.Pipeline, 'nml.Pipeline']:
        """Create a new PipelineSpec given extra parameters.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :return: a new PipelineSpec
        """
        # TODO: having a different pipeline class for ones with a y_transformer
        # is a bit ugly.
        objs = self.objects
        y_trans_objs = [o for o in self.objects if o.spec_class == YTRANS_NAME]
        if y_trans_objs:
            objs = [o for o in self.objects if o.spec_class != YTRANS_NAME]

        pipe = PipelineSpec._instantiate_steps(objs, problem_info, random_state=random_state,
                                               pipeline_module=self.module, pipeline_class_name=self.class_name)

        if y_trans_objs:
            for ytrans in y_trans_objs:
                pipe = model_wrappers.PipelineWithYTransformations(
                    pipe, ytrans.class_name, ytrans.instantiate(
                        problem_info,
                        random_state=random_state,
                        num_threads=problem_info.num_threads))

        return pipe

    @staticmethod
    def _instantiate_steps(spec_steps: List[ObjectSpec],
                           problem_info: ProblemInfo,
                           random_state: Optional[int] = None,
                           pipeline_module: str = SK_PIPELINE_MODULE,
                           pipeline_class_name: str = SK_PIPELINE_CLASS_NAME) -> Union[pipeline.Pipeline, Any]:
        """
        Instantiate all steps in the pipeline.

        This function ensures that preprocessors ignore categorical columns when
        they are in problem info and the final estimator of the pipeline can
        accept categorical columns.

        :param spec_steps: List of steps in the pipeline spec.
        :param problem_info: Problem metadata
        :param random_state:
        :return: List of instantiated pipeline steps.
        """
        has_categoricals = problem_info.dataset_categoricals is not None
        categorical_params = constants.ModelParameters.CATEGORICAL_FEATURES
        accepts_categoricals = spec_steps[-1].class_name in categorical_params

        steps = []
        for spec_step in spec_steps:
            class_name = spec_step.class_name

            # Check if the dataset has categoricals, the pipeline accepts categorical indicators,
            # and this is a preprocessing step, not the final estimator
            if has_categoricals and accepts_categoricals and class_name not in categorical_params:
                preprocessor = PipelineSpec._instantiate_step(spec_step, problem_info, random_state)
                step = PipelineSpec._wrap_categorical_preprocessor(preprocessor, problem_info)
            else:
                step = PipelineSpec._instantiate_step(spec_step, problem_info, random_state)

            steps.append((class_name, step))

        mod = importlib.import_module(pipeline_module)
        cls = getattr(mod, pipeline_class_name)
        return cls(steps)

    @staticmethod
    def _instantiate_step(spec_step: ObjectSpec,
                          problem_info: ProblemInfo,
                          random_state: Optional[int]) -> Any:
        return spec_step.instantiate(problem_info,
                                     random_state=random_state,
                                     num_threads=problem_info.num_threads)

    @staticmethod
    def _make_categoricals(n_categorical, n_numerical):
        return np.concatenate((np.full((n_categorical,), True, dtype=bool),
                               np.full((n_numerical,), False, dtype=bool)), axis=0)

    @staticmethod
    def _wrap_categorical_preprocessor(preprocessor: Any,
                                       problem_info: ProblemInfo) -> Any:
        """
        Wrap a preprocessor so that all categorical columns are ignored.

        :param preprocessor: Preprocessor wrapper object.
        :param problem_info: Problem metadata that hold the categorical indicators.
        :return: New pipeline step, conditional on the types of features.
        """
        numericals = ~problem_info.dataset_categoricals
        categorical_indices = np.where(problem_info.dataset_categoricals)[0]
        numerical_indices = np.where(numericals)[0]

        def get_categorical_columns(X):
            return X[:, problem_info.dataset_categoricals]

        def get_numerical_columns(X):
            return X[:, numericals]

        def update_categoricals(X):
            total_features = X.shape[1]
            n_categorical = len(categorical_indices)
            n_numerical = total_features - n_categorical
            problem_info.pipeline_categoricals = PipelineSpec._make_categoricals(n_categorical, n_numerical)
            return X

        # 1) Split the features into categorical and numerical
        # 2) Apply the preprocessor only to the numerical features
        # 3) Merge the features back together in their original order
        func_trans = preprocessing.FunctionTransformer
        id_trans = model_wrappers.IdentityTransformer()
        parts = []
        if categorical_indices.shape[0] != 0:
            parts.append(pipeline.make_pipeline(func_trans(get_categorical_columns, validate=True), id_trans))
        if numerical_indices.shape[0] != 0:
            parts.append(pipeline.make_pipeline(func_trans(get_numerical_columns, validate=True), preprocessor))
        union_pipe = pipeline.make_union(*parts)
        ordered_pipe = pipeline.make_pipeline(union_pipe, func_trans(update_categoricals, validate=True))
        return ordered_pipe
