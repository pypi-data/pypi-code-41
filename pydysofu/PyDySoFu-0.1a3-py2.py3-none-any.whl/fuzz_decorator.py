"""
@author probablytom
@author twsswt
"""

from core_fuzzers import identity

from fuzz_weaver import fuzz_function


fuzz_decorators = dict()


# noinspection PyPep8Naming
class fuzz(object):
    """
    A general purpose decorator for applying fuzzings to functions containing workflow steps.

    Attributes:
    enable_fuzzings is by default set to True, but can be set to false to globally disable fuzzing.
    """

    enable_fuzzings = True

    def __init__(self, fuzzer=identity, label=None):
        self.fuzzer = fuzzer
        self.label = label
        self._original_syntax_tree = None

    def __call__(self, func):

        if self.label is not None and self.label not in fuzz_decorators.keys():
            fuzz_decorators[self.label] = self

        def wrap(*args, **kwargs):

            if not fuzz.enable_fuzzings:
                return func(*args, **kwargs)

            fuzz_function(func, self.fuzzer)

            # Execute the mutated function.
            return func(*args, **kwargs)

        wrap.func_name = func.func_name
        wrap.func_dict = func.func_dict
        return wrap



def set_fuzzer(target_label, fuzzer):
    '''
    Allows fuzzers to be hotswapped on decorated targets, by looking up the decorator object in the `fuzz_decorators`
    mapping in this file and changing the `<decorator object/>.fuzzer` attribute. Returns either an exception indicating
    failure, or None for a success.
    :param target: The label for the thing being fuzzed.
    :param fuzzer: The fuzzer we want to apply from now on
    :return: Exception for failure, None for success.
    '''
    try:
        fuzz_decorators[target_label].fuzzer = fuzzer
    except Exception as e:
        return e