from edc_lab import RequisitionPanel

from .processing_profiles import (
    fbc_processing,
    hba1c_processing,
    chemistry_processing,
    chemistry_alt_processing,
    blood_glucose_processing,
)


hb1ac_panel = RequisitionPanel(
    name="hba1c", verbose_name="Hemoglogin A1c", processing_profile=hba1c_processing
)


fbc_panel = RequisitionPanel(
    name="fbc", verbose_name="Full Blood Count", processing_profile=fbc_processing
)

blood_glucose_panel = RequisitionPanel(
    name="blood_glucose",
    verbose_name="Blood Glucose",
    processing_profile=blood_glucose_processing,
)

chemistry_panel = RequisitionPanel(
    name="chemistry",
    verbose_name="Creat, Urea, Elec",
    processing_profile=chemistry_processing,
)

chemistry_alt_panel = RequisitionPanel(
    name="chemistry_alt",
    verbose_name="Creat, Urea, Elec, ALT",
    processing_profile=chemistry_alt_processing,
)
