# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model, the extended attributes for Excel
    output and columns titles in FRENCH.
"""

# ##############################################################################
# ############ Globals ############
# #################################

I18N_EN = {
    # worksheets
    "attributes": "Feature Attributes",
    "dashboard": "Dashboard",
    "raster": "Rasters",
    "resource": "Ressources",
    "service": "Services",
    "vector": "Vectors",
    # metadata model
    "_created": "MD - Creation date",
    "_creator": "Owner",
    "_id": "MD - UUID",
    "_modified": "MD - Update date",
    "abstract": "Abstract",
    "collectionContext": "Collect context",
    "collectionMethod": "Collect method",
    "conditions": "CGUs",
    "contacts": "Contacts",
    "coordinateSystem": "SRS (EPSG)",
    "created": "Creation date",
    "distance": "Resolution",
    "editionProfile": "Source",
    "encoding": "Encoding",
    "envelope": "Bounding box",
    "events": "# Updates",
    "featureAttributes": "Feature attributes (A-Z)",
    "features": "# objects",
    "format": "Format",
    "formatVersion": "Version",
    "geometry": "Geometry",
    "keywords": "Keywords",
    "language": "Language",
    "layers": "Layers",
    "limitations": "Limitations",
    "links": "Links",
    "modified": "Last update",
    "name": "Technical name",
    "operations": "Operations",
    "path": "Location",
    "precision": "Precision",
    "published": "Publication date",
    "scale": "EchellScale",
    "series": "Set of dataset",
    "serviceLayers": "associated layers",
    "specifications": "Specifications",
    "tags": "Tags",
    "title": "Title",
    "topologicalConsistency": "Topological consistency",
    "type": "Type",
    "updateFrequency": "Update frequency",
    "validFrom": "Start date of validity",
    "validTo": "End date of validity",
    "validityComment": "Validity comment",
    # specific
    "featureAttributesCount": "# feature attributes",
    "hasLinkDownload": "Downloadable",
    "hasLinkOther": "Others links",
    "hasLinkView": "Viewable",
    "linkEdit": "Edit",
    "linkView": "See online",
    "inspireConformance": "INSPIRE conformance",
    "inspireThemes": "INSPIRE themes",
    "occurrences": "Hits",
}

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """ Standalone execution and development tests """
    # specific imports
    columns_fr = I18N_EN
    assert columns_fr.get("title") == "Title"
