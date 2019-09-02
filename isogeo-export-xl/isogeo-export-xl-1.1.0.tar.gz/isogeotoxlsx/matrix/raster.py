# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
RASTER_COLUMNS = {
    "_created": ("AI", 0),
    "_creator": ("E", 0),
    "_id": ("AH", 0),
    "_modified": ("AJ", 0),
    "abstract": ("C", 0),
    "collectionContext": ("I", 0),
    "collectionMethod": ("J", 0),
    "conditions": ("Z", 0),
    "contacts": ("AB", 0),
    "coordinateSystem": ("T", 0),
    "created": ("O", 0),
    "distance": ("V", 0),
    "editionProfile": (None, 0),
    "encoding": (None, 0),
    "envelope": ("U", 0),
    "events": ("P", 0),
    "featureAttributes": (None, 0),
    "features": ("Y", 0),
    "format": ("S", 0),
    "formatVersion": (None, 0),
    "geometry": (None, 0),
    "keywords": ("F", 0),
    "language": ("AK", 0),
    "layers": (None, 0),
    "limitations": ("AA", 0),
    "links": (None, 0),
    "modified": ("Q", 0),
    "name": ("B", 0),
    "operations": (None, 0),
    "path": ("D", 0),
    "precision": (None, 0),
    "published": (None, 0),
    "scale": ("X", 0),
    "series": (None, 0),
    "serviceLayers": (None, 0),
    "specifications": ("X", 0),
    "tags": (None, 0),
    "title": ("A", 0),
    "topologicalConsistency": ("AC", 0),
    "type": (None, 0),
    "updateFrequency": ("M", 0),
    "validFrom": ("K", 0),
    "validTo": ("L", 0),
    "validityComment": ("N", 0),
    # specific
    "hasLinkDownload": ("AC", 0),
    "hasLinkOther": ("AE", 0),
    "hasLinkView": ("AD", 0),
    "linkEdit": ("AF", 0),
    "linkView": ("AG", 0),
    "inspireConformance": ("H", 0),
    "inspireThemes": ("G", 0),
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
    print(isinstance(columns_vector.get("title"), Column))
