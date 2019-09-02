# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
RESOURCE_COLUMNS = {
    "_created": ("T", 0),
    "_creator": ("D", 0),
    "_id": ("S", 0),
    "_modified": ("U", 0),
    "abstract": ("B", 0),
    "conditions": ("K", 0),
    "contacts": ("M", 0),
    "created": ("F", 0),
    "format": ("J", 0),
    "keywords": ("E", 0),
    "language": ("V", 0),
    "limitations": ("L", 0),
    "links": (None, 0),
    "modified": ("H", 0),
    "name": ("Z", 0),
    "path": ("C", 0),
    "published": ("I", 0),
    "specifications": ("AB", 0),
    "tags": (None, 0),
    "title": ("A", 0),
    # specific
    "hasLinkDownload": ("N", 0),
    "hasLinkOther": ("P", 0),
    "hasLinkView": ("O", 0),
    "linkEdit": ("Q", 0),
    "linkView": ("R", 0),
    "inspireConformance": ("Y", 0),
    "inspireThemes": ("X", 0),
}

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """ Standalone execution and development tests """
    # specific imports
    from collections import namedtuple

    # set namedtuple structure
    Column = namedtuple("Column", ["letter", "title", "wrap"])
    # apply transformation
    columns_vector = {k: Column._make(v) for k, v in RESOURCE_COLUMNS.items()}
    # check
    print(isinstance(columns_vector, dict))
    print(isinstance(columns_vector.get("title"), Column))
