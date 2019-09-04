# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model and Excel columns for Isogeo to Office.
"""

# ##############################################################################
# ############ Globals ############
# #################################
VECTOR_COLUMNS = {
    "_created": ("AM", "date", 15),
    "_creator": ("E", None, 30),
    "_id": ("AL", None, 15),
    "_modified": ("AN", "date", 15),
    "abstract": ("C", "wrap", 50),
    "collectionContext": ("I", "wrap", 15),
    "collectionMethod": ("J", "wrap", 15),
    "conditions": ("AD", "wrap", 15),
    "contacts": ("AF", None, 15),
    "coordinateSystem": ("T", None, 30),
    "created": ("O", "date", 15),
    "distance": ("W", None, 15),
    "editionProfile": (None, None, 15),
    "encoding": (None, None, 15),
    "envelope": ("U", "wrap", 15),
    "events": ("P", None, 15),
    "featureAttributes": ("AA", "wrap", 15),
    "features": ("Y", None, 15),
    "format": ("S", None, 15),
    "formatVersion": (None, None, 15),
    "geometry": ("V", None, 15),
    "keywords": ("F", "wrap", 15),
    "language": ("AO", None, 15),
    "layers": (None, None, 15),
    "limitations": ("AE", "wrap", 15),
    "links": (None, None, 15),
    "modified": ("Q", "date", 15),
    "name": ("B", None, 15),
    "operations": (None, None, 15),
    "path": ("D", None, 15),
    "precision": (None, None, 15),
    "published": ("R", "date", 15),
    "scale": ("X", None, 15),
    "series": (None, None, 15),
    "serviceLayers": (None, None, 15),
    "specifications": ("AB", "wrap", 15),
    "tags": (None, None, 15),
    "title": ("A", None, 50),
    "topologicalConsistency": ("AC", "wrap", 15),
    "type": (None, None, 15),
    "updateFrequency": ("M", None, 15),
    "validFrom": ("K", "date", 15),
    "validTo": ("L", "date", 15),
    "validityComment": ("N", None, 15),
    # specific,
    "featureAttributesCount": ("Z", None, 15),
    "hasLinkDownload": ("AG", None, 15),
    "hasLinkOther": ("AI", None, 15),
    "hasLinkView": ("AH", None, 15),
    "linkEdit": ("AJ", None, 15),
    "linkView": ("AK", None, 15),
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
    Column = namedtuple("Column", ["letter", "wrap"])
    # apply transformation
    columns_vector = {k: Column._make(v) for k, v in VECTOR_COLUMNS.items()}
    # check
    print(isinstance(columns_vector, dict))
    print(isinstance(columns_vector.get("title", 15), Column))

    for k, v in columns_vector.items():
        print(k, type(v, 15), v.letter)
