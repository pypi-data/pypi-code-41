# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
SERVICE_COLUMNS = {
    "_created": ("X", 0),
    "_creator": ("E", 0),
    "_id": ("W", 0),
    "_modified": ("Y", 0),
    "abstract": ("C", 0),
    "collectionContext": ("I", 0),
    "collectionMethod": ("J", 0),
    "conditions": ("O", 0),
    "contacts": ("Q", 0),
    "coordinateSystem": (None, 0),
    "created": ("H", 0),
    "distance": (None, 0),
    "editionProfile": (None, 0),
    "encoding": (None, 0),
    "envelope": ("M", 0),
    "events": ("I", 0),
    "featureAttributes": (None, 0),
    "features": ("Y", 0),
    "format": ("L", 0),
    "formatVersion": (None, 0),
    "geometry": (None, 0),
    "keywords": ("F", 0),
    "language": ("AQZ", 0),
    "layers": (None, 0),
    "limitations": ("P", 0),
    "links": (None, 0),
    "modified": ("J", 0),
    "name": ("B", 0),
    "operations": (None, 0),
    "path": ("D", 0),
    "precision": (None, 0),
    "published": ("K", 0),
    "scale": ("X", 0),
    "series": (None, 0),
    "serviceLayers": (None, 0),
    "specifications": ("N", 0),
    "tags": (None, 0),
    "title": ("A", 0),
    "topologicalConsistency": ("AC", 0),
    "type": (None, 0),
    "updateFrequency": (None, 0),
    "validFrom": (None, 0),
    "validTo": (None, 0),
    "validityComment": (None, 0),
    # specific
    "hasLinkDownload": ("R", 0),
    "hasLinkOther": ("T", 0),
    "hasLinkView": ("S", 0),
    "linkEdit": ("U", 0),
    "linkView": ("V", 0),
    "inspireConformance": ("G", 0),
    "inspireThemes": (None, 0),
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
    print(isinstance(columns_vector.get("title"), Column))
