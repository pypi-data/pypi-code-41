# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
VECTOR_COLUMNS = {
    "_created": ("AM", 0),
    "_creator": ("E", 0),
    "_id": ("AL", 0),
    "_modified": ("AN", 0),
    "abstract": ("C", 0),
    "collectionContext": ("I", 0),
    "collectionMethod": ("J", 0),
    "conditions": ("AD", 0),
    "contacts": ("AF", 0),
    "coordinateSystem": ("T", 0),
    "created": ("O", 0),
    "distance": ("W", 0),
    "editionProfile": (None, 0),
    "encoding": (None, 0),
    "envelope": ("U", 0),
    "events": ("P", 0),
    "featureAttributes": ("AA", 0),
    "features": ("Y", 0),
    "format": ("S", 0),
    "formatVersion": (None, 0),
    "geometry": ("V", 0),
    "keywords": ("F", 0),
    "language": ("AO", 0),
    "layers": (None, 0),
    "limitations": ("AE", 0),
    "links": (None, 0),
    "modified": ("Q", 0),
    "name": ("B", 0),
    "operations": (None, 0),
    "path": ("D", 0),
    "precisio(n": (None, 0),
    "published": ("R", 0),
    "scale": ("X", 0),
    "series": (None, 0),
    "serviceLayers": (None, 0),
    "specifications": ("AB", 0),
    "tags": (None, 0),
    "title": ("A", 0),
    "topologicalConsistency": ("AC", 0),
    "typ(e": (None, 0),
    "updateFrequency": ("M", 0),
    "validFrom": ("K", 0),
    "validTo": ("L", 0),
    "validityComment": ("N", 0),
    # specific,
    "featureAttributesCount": ("Z", 0),
    "hasLinkDownload": ("AG", 0),
    "hasLinkOther": ("AI", 0),
    "hasLinkView": ("AH", 0),
    "linkEdit": ("AJ", 0),
    "linkView": ("AK", 0),
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
    Column = namedtuple("Column", ["letter", "wrap"])
    # apply transformation
    columns_vector = {k: Column._make(v) for k, v in VECTOR_COLUMNS.items()}
    # check
    print(isinstance(columns_vector, dict))
    print(isinstance(columns_vector.get("title"), Column))

    for k, v in columns_vector.items():
        print(k, type(v), v.letter)
