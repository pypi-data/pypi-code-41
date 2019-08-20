"""Functions used for class registration."""
# import logging
# import re
# from .globals import global_vars


# def register(cls):
#     """Register class."""
#     classname = cls.__name__
#     if classname in globals() and 'Wrapped(' not in classname:
#         raise ValueError('{} is already a registered class.'.format(classname))
#     print('register: ', classname)
#     global_vars[classname] = cls
#     print(global_vars)
#     # globals()[classname] = cls


# def unregister(cls):
#     """Unregister class."""
#     classname = cls if isinstance(cls, str) else cls.__name__
#     print(global_vars)
#     if classname in global_vars:
#         global_vars.pop(classname)
#     else:
#         logging.warning('{} is not a registered class'.format(classname))


# def unregister_all():
#     """Unregister all classes."""
#     for classname in get_registered_wrappers_classnames():
#         unregister(classname)


# def get_registered_wrappers_classnames():
#     """Get classnames of all registered wrappers."""
#     return list(set([k for k in global_vars if 'Wrapped' in k]))


# def make_wrapper_classname(classname):
#     """Return new wrapper classname based on registered classes."""
#     registered_wrappers = get_registered_wrappers_classnames()
#     searches = [re.search(r'Wrapped([0-9]*)\((.*)\)', elt)
#                 for elt in registered_wrappers]
#     nums = [search.groups()[0] for search in searches
#             if search is not None and search.groups() is not None]
#     if len(nums) == 0:
#         wrapper_classname = 'Wrapped({})'.format(classname)
#     else:
#         if len(nums) == 1 and nums[0] == '':
#             max_num = 2
#             wrapper_classname = 'Wrapped{}({})'.format(max_num, classname)
#         else:
#             nums = [int(num) for num in nums if num != '']
#             max_num = sorted(nums)[-1] + 1
#             wrapper_classname = 'Wrapped{}({})'.format(max_num, classname)
#     return wrapper_classname
