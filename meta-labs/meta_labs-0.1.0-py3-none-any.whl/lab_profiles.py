from edc_lab import LabProfile

from .panels import (
    fbc_panel,
    blood_glucose_panel,
    hb1ac_panel,
    chemistry_panel,
    chemistry_alt_panel,
)


subject_lab_profile = LabProfile(
    name="subject_lab_profile", requisition_model="meta_subject.subjectrequisition"
)

subject_lab_profile.add_panel(fbc_panel)
subject_lab_profile.add_panel(blood_glucose_panel)
subject_lab_profile.add_panel(hb1ac_panel)
subject_lab_profile.add_panel(chemistry_panel)
subject_lab_profile.add_panel(chemistry_alt_panel)
