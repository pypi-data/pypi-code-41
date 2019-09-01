from edc_permissions.codenames import auditor

auditor += [
    "edc_dashboard.view_screening_listboard",
    "edc_dashboard.view_subject_listboard",
    "edc_navbar.nav_screening_section",
    "edc_navbar.nav_subject_section",
    "meta_ae.view_aefollowup",
    "meta_ae.view_aeinitial",
    "meta_ae.view_historicalaefollowup",
    "meta_ae.view_historicalaeinitial",
    "meta_prn.view_deathreport",
    "meta_prn.view_historicaldeathreport",
    "meta_prn.view_historicalonschedule",
    "meta_prn.view_historicalprotocoldeviationviolation",
    "meta_prn.view_historicalstudyterminationconclusion",
    "meta_prn.view_onschedule",
    "meta_prn.view_protocoldeviationviolation",
    "meta_prn.view_studyterminationconclusion",
]
auditor.sort()
