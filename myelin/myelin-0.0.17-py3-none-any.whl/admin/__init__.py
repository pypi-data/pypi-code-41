from myelin.admin.myelin_admin import MyelinAdmin
import os

__ADMIN_CLIENT__ = MyelinAdmin()


def data_path(default_value=None):
    return os.environ.get('DATA_PATH') or default_value


def model_path(default_value=None):
    return os.environ.get('MODEL_PATH') or default_value


def model_backend(axon, model_graph, model, model_backend, namespace, default_value=None):
    return __ADMIN_CLIENT__.model_backend(axon, model_graph, model, model_backend, namespace, default_value)
