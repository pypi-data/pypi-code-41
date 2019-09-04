# -*- coding: UTF-8 -*-
#! python3

"""
    Matching table between Isogeo metadata model, the extended attributes for Excel
    output and columns titles in FRENCH.
"""

# ##############################################################################
# ############ Globals ############
# #################################

I18N_FR = {
    # worksheets
    "attributes": "Attributs",
    "dashboard": "Tableau de bord",
    "raster": "Rasters",
    "resource": "Ressources",
    "service": "Services",
    "vector": "Vecteurs",
    # metadata model
    "_created": "MD - Date de création",
    "_creator": "Propriétaire",
    "_id": "MD - UUID",
    "_modified": "MD - Modification",
    "abstract": "Résumé",
    "collectionContext": "Contexte de collecte",
    "collectionMethod": "Méthode de collecte",
    "conditions": "CGUs",
    "contacts": "Contacts",
    "coordinateSystem": "SRS (EPSG)",
    "created": "Date de création",
    "distance": "Résolution",
    "editionProfile": "Source",
    "encoding": "Encodage des données",
    "envelope": "Emprise",
    "events": "# Mises à jour",
    "featureAttributes": "Attributs (A-Z)",
    "features": "# objets",
    "format": "Format",
    "formatVersion": "Version",
    "geometry": "Géométrie",
    "keywords": "Mots-clés",
    "language": "Langue",
    "layers": "Couches de services",
    "limitations": "Limitations",
    "links": "Liens",
    "modified": "Dernière mise à jour",
    "name": "Nom technique",
    "operations": "Opérations",
    "path": "Emplacement",
    "precision": "Précision",
    "published": "Date de publication",
    "scale": "Echelle",
    "series": "Série de données",
    "serviceLayers": "Couches associées",
    "specifications": "Spécifications",
    "tags": "Etiquettes",
    "title": "Titre",
    "topologicalConsistency": "Cohérence topolgique",
    "type": "Type",
    "updateFrequency": "Fréquence de mise à jour",
    "validFrom": "Début de validité",
    "validTo": "Fin de validité",
    "validityComment": "Commentaire",
    # specific
    "featureAttributesCount": "# Attributs",
    "hasLinkDownload": "Téléchargeable",
    "hasLinkOther": "Autres liens",
    "hasLinkView": "Visualisable",
    "linkEdit": "Editer",
    "linkView": "Consulter",
    "inspireConformance": "Conformité INSPIRE",
    "inspireThemes": "Thématique(s) INSPIRE",
    "occurrences": "Occurrences",
}

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """ Standalone execution and development tests """
    # specific imports
    columns_fr = I18N_FR
    assert columns_fr.get("title") == "Titre"
