from edc_permissions.codenames import pii_view

pii_view += [
    "meta_screening.view_historicalsubjectscreening",
    "meta_screening.view_subjectscreening",
    "meta_consent.view_historicalsubjectreconsent",
    "meta_consent.view_subjectreconsent",
]

pii_view.sort()
