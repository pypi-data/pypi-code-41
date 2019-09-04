# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table of Excel columns for Feature Attributes analisis.
"""

# ##############################################################################
# ############ Globals ############
# #################################
ATTRIBUTES_COLUMNS = {"name": ("A", None, 40), "occurrences": ("B", None, 15)}

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """ Standalone execution and development tests """
    # specific imports
    from collections import namedtuple

    # set namedtuple structure
    Column = namedtuple("Column", ["letter", "wrap"])
    # apply transformation
    columns_ref = {k: Column._make(v) for k, v in ATTRIBUTES_COLUMNS.items()}
    # check
    print(isinstance(columns_ref, dict))
    print(isinstance(columns_ref.get("name"), Column))

    for k, v in columns_ref.items():
        print(k, type(v), v.letter)
