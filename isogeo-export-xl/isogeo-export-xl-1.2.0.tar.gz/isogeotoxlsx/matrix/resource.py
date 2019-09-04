# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
RESOURCE_COLUMNS = {
    "_created": ("T", "date", 15),
    "_creator": ("D", None, 30),
    "_id": ("S", None, 15),
    "_modified": ("U", "date", 15),
    "abstract": ("B", "wrap", 50),
    "conditions": ("K", "wrap", 15),
    "contacts": ("M", None, 15),
    "created": ("F", "date", 15),
    "format": ("J", None, 15),
    "keywords": ("E", "wrap", 15),
    "language": ("V", None, 15),
    "limitations": ("L", "wrap", 15),
    "links": (None, None, 15),
    "modified": ("H", "date", 15),
    "name": ("Z", None, 15),
    "path": ("C", None, 15),
    "published": ("I", "date", 15),
    "specifications": ("AB", "wrap", 15),
    "tags": (None, None, 15),
    "title": ("A", None, 50),
    # specific
    "hasLinkDownload": ("N", None, 15),
    "hasLinkOther": ("P", None, 15),
    "hasLinkView": ("O", None, 15),
    "linkEdit": ("Q", None, 15),
    "linkView": ("R", None, 15),
    "inspireConformance": ("Y", None, 15),
    "inspireThemes": ("X", "wrap", 15),
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
    print(isinstance(columns_vector.get("title", 15), Column))
