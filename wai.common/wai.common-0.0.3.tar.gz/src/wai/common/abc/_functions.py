from typing import Tuple, Dict, Any


def get_abstract_methods(bases: Tuple, namespace: Dict[str, Any]):
    """
    Gets the names of the abstract methods that will result from
    a class created with the given base-class set and namespace.

    :param bases:       The base-class set.
    :param namespace:   The namespace.
    :return:            The set of abstract method names.
    """
    abstract_methods = set()

    for base in bases:
        abstract_methods.update(getattr(base, '__abstractmethods__', set()))

    for name, value in namespace.items():
        if is_abstract_function(value):
            abstract_methods.add(name)
        else:
            if name in abstract_methods:
                abstract_methods.remove(name)

    return abstract_methods


def will_be_abstract(bases: Tuple, namespace: Dict[str, Any]):
    """
    Determines if a class made with the given set of base-classes
    and namespace will be abstract or concrete.

    :param bases:       The set of base classes.
    :param namespace:   The namespace of the new class.
    :return:            True if the newly-created class will be abstract,
                        False if it will be concrete.
    """
    return len(get_abstract_methods(bases, namespace)) > 0


def is_abstract_function(func):
    """
    Whether the given function is abstract in its class.

    :param func:    The function to check.
    :return:        True if the function is abstract,
                    False if not.
    """
    return getattr(func, '__isabstractmethod__', False)
