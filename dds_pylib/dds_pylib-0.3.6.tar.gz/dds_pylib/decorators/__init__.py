'''
from subpackage import * -  is frowned upon, don't add any submodules to __all__
'''
__all__ = []

# import to make these available at the package level
from annotate import annotate
from deprecated import deprecated
from time_decorators import timeit
from static_vars import static_vars