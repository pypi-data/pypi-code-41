# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
SERVICE_COLUMNS = {
    "_created": ("X", "date", 15),
    "_creator": ("E", None, 30),
    "_id": ("W", None, 15),
    "_modified": ("Y", "date", 15),
    "abstract": ("C", "wrap", 50),
    "collectionContext": ("I", "wrap", 15),
    "collectionMethod": ("J", "wrap", 15),
    "conditions": ("O", "wrap", 15),
    "contacts": ("Q", None, 15),
    "coordinateSystem": (None, None, 30),
    "created": ("H", "date", 15),
    "distance": (None, None, 15),
    "editionProfile": (None, None, 15),
    "encoding": (None, None, 15),
    "envelope": ("M", "wrap", 15),
    "events": ("I", None, 15),
    "featureAttributes": (None, None, 15),
    "features": ("Y", None, 15),
    "format": ("L", None, 15),
    "formatVersion": (None, None, 15),
    "geometry": (None, None, 15),
    "keywords": ("F", "wrap", 15),
    "language": ("AQZ", None, 15),
    "layers": (None, None, 15),
    "limitations": ("P", "wrap", 15),
    "links": (None, None, 15),
    "modified": ("J", "date", 15),
    "name": ("B", None, 15),
    "operations": (None, None, 15),
    "path": ("D", None, 15),
    "precision": (None, None, 15),
    "published": ("K", "date", 15),
    "scale": ("X", None, 15),
    "series": (None, None, 15),
    "serviceLayers": (None, None, 15),
    "specifications": ("N", "wrap", 15),
    "tags": (None, None, 15),
    "title": ("A", None, 50),
    "topologicalConsistency": ("AC", "wrap", 15),
    "type": (None, None, 15),
    "updateFrequency": (None, None, 15),
    "validFrom": (None, "date", 15),
    "validTo": (None, "date", 15),
    "validityComment": (None, None, 15),
    # specific
    "hasLinkDownload": ("R", None, 15),
    "hasLinkOther": ("T", None, 15),
    "hasLinkView": ("S", None, 15),
    "linkEdit": ("U", None, 15),
    "linkView": ("V", None, 15),
    "inspireConformance": ("G", None, 15),
    "inspireThemes": (None, "wrap", 15),
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
    columns_vector = {k: Column._make(v) for k, v in SERVICE_COLUMNS.items()}
    # check
    print(isinstance(columns_vector, dict))
    print(isinstance(columns_vector.get("title", 15), Column))
