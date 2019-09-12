"""
Import Tools
"""
import importlib


def import_object_from_path(object_path):
    """

    Args:
        object_path: 对象路径

    Returns:
        Object
    """
    object_module_path, object_name = object_path.rsplit('.', 1)
    module = importlib.import_module(object_module_path)
    return getattr(module, object_name)
