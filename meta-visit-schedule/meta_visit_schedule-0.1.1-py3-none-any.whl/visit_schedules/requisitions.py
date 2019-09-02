from edc_visit_schedule import FormsCollection, Requisition
from meta_labs import (
    fbc_panel,
    chemistry_panel,
    chemistry_alt_panel,
    blood_glucose_panel,
)


requisitions_prn = FormsCollection(
    Requisition(
        show_order=10, panel=blood_glucose_panel, required=True, additional=False
    ),
    Requisition(show_order=20, panel=fbc_panel, required=True, additional=False),
    Requisition(show_order=40, panel=chemistry_panel, required=True, additional=False),
    Requisition(
        show_order=50, panel=chemistry_alt_panel, required=True, additional=False
    ),
    name="requisitions_prn",
)

requisitions_d1 = FormsCollection(
    Requisition(
        show_order=10, panel=blood_glucose_panel, required=True, additional=False
    ),
    Requisition(show_order=20, panel=fbc_panel, required=True, additional=False),
    name="requisitions_day1",
)

requisitions_3m = FormsCollection(
    Requisition(
        show_order=10, panel=blood_glucose_panel, required=True, additional=False
    ),
    Requisition(show_order=20, panel=chemistry_panel, required=True, additional=False),
    name="requisitions_month3",
)

requisitions_6m = FormsCollection(
    Requisition(
        show_order=10, panel=blood_glucose_panel, required=True, additional=False
    ),
    Requisition(show_order=20, panel=chemistry_panel, required=True, additional=False),
    name="requisitions_default",
)

requisitions_9m = FormsCollection(
    Requisition(
        show_order=10, panel=blood_glucose_panel, required=True, additional=False
    ),
    Requisition(show_order=20, panel=chemistry_panel, required=True, additional=False),
    name="requisitions_month97",
)

requisitions_12m = FormsCollection(
    Requisition(
        show_order=10, panel=blood_glucose_panel, required=True, additional=False
    ),
    Requisition(show_order=20, panel=fbc_panel, required=True, additional=False),
    Requisition(
        show_order=30, panel=chemistry_alt_panel, required=True, additional=False
    ),
    name="requisitions_month12",
)
