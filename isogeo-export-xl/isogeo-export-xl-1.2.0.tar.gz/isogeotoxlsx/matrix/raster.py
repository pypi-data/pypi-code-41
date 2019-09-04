# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
RASTER_COLUMNS = {
    "_created": ("AI", "date", 15),
    "_creator": ("E", None, 30),
    "_id": ("AH", None, 15),
    "_modified": ("AJ", "date", 15),
    "abstract": ("C", "wrap", 50),
    "collectionContext": ("I", None, 15),
    "collectionMethod": ("J", None, 15),
    "conditions": ("Z", "wrap", 15),
    "contacts": ("AB", None, 15),
    "coordinateSystem": ("T", None, 30),
    "created": ("O", "date", 15),
    "distance": ("V", None, 15),
    "editionProfile": (None, None, 15),
    "encoding": (None, None, 15),
    "envelope": ("U", "wrap", 15),
    "events": ("P", None, 15),
    "featureAttributes": (None, None, 15),
    "features": ("Y", None, 15),
    "format": ("S", None, 15),
    "formatVersion": (None, None, 15),
    "geometry": (None, None, 15),
    "keywords": ("F", "wrap", 15),
    "language": ("AK", None, 15),
    "layers": (None, None, 15),
    "limitations": ("AA", "wrap", 15),
    "links": (None, None, 15),
    "modified": ("Q", "date", 15),
    "name": ("B", None, 15),
    "operations": (None, None, 15),
    "path": ("D", None, 15),
    "precision": (None, None, 15),
    "published": (None, "date", 15),
    "scale": ("X", None, 15),
    "series": (None, None, 15),
    "serviceLayers": (None, None, 15),
    "specifications": ("X", None, 15),
    "tags": (None, None, 15),
    "title": ("A", None, 50),
    "topologicalConsistency": ("AC", None, 15),
    "type": (None, None, 15),
    "updateFrequency": ("M", None, 15),
    "validFrom": ("K", "date", 15),
    "validTo": ("L", "date", 15),
    "validityComment": ("N", None, 15),
    # specific
    "hasLinkDownload": ("AC", None, 15),
    "hasLinkOther": ("AE", None, 15),
    "hasLinkView": ("AD", None, 15),
    "linkEdit": ("AF", None, 15),
    "linkView": ("AG", None, 15),
    "inspireConformance": ("H", None, 15),
    "inspireThemes": ("G", "wrap", 15),
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
    columns_vector = {k: Column._make(v) for k, v in RASTER_COLUMNS.items()}
    # check
    print(isinstance(columns_vector, dict))
    print(isinstance(columns_vector.get("title", 15), Column))
