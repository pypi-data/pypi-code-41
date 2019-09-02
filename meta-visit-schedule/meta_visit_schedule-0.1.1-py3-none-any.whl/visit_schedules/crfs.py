from edc_visit_schedule import FormsCollection, Crf

crfs_prn = FormsCollection(
    Crf(show_order=10, model="meta_subject.bloodresultsglu"),
    Crf(show_order=20, model="meta_subject.bloodresultsfbc"),
    Crf(show_order=30, model="meta_subject.bloodresultslft"),
    Crf(show_order=40, model="meta_subject.bloodresultsrft"),
    name="prn",
)

crfs_unscheduled = FormsCollection(
    Crf(show_order=10, model="meta_subject.bloodresultsglu"),
    Crf(show_order=20, model="meta_subject.bloodresultsfbc"),
    Crf(show_order=30, model="meta_subject.bloodresultslft"),
    Crf(show_order=40, model="meta_subject.bloodresultsrft"),
    Crf(show_order=50, model="meta_subject.malariarapidtest"),
    Crf(show_order=60, model="meta_subject.urinedipsticktest"),
    name="unscheduled",
)


crfs_d1 = FormsCollection(
    Crf(show_order=10, model="meta_subject.bloodresultsglu"),
    Crf(show_order=20, model="meta_subject.bloodresultsfbc"),
    Crf(show_order=30, model="meta_subject.bloodresultslft"),
    Crf(show_order=40, model="meta_subject.bloodresultsrft"),
    Crf(show_order=50, model="meta_subject.urinedipsticktest"),
    name="day1",
)

crfs_3m = FormsCollection(
    Crf(show_order=10, model="meta_subject.bloodresultsglu"),
    Crf(show_order=20, model="meta_subject.bloodresultsfbc"),
    Crf(show_order=30, model="meta_subject.bloodresultslft"),
    Crf(show_order=40, model="meta_subject.bloodresultsrft"),
    Crf(show_order=50, model="meta_subject.urinedipsticktest"),
    name="3m",
)

crfs_6m = FormsCollection(
    Crf(show_order=10, model="meta_subject.bloodresultsglu"),
    Crf(show_order=20, model="meta_subject.bloodresultsfbc"),
    Crf(show_order=30, model="meta_subject.bloodresultslft"),
    Crf(show_order=40, model="meta_subject.bloodresultsrft"),
    Crf(show_order=50, model="meta_subject.urinedipsticktest"),
    name="6m",
)

crfs_9m = FormsCollection(
    Crf(show_order=10, model="meta_subject.bloodresultsglu"),
    Crf(show_order=20, model="meta_subject.bloodresultsfbc"),
    Crf(show_order=30, model="meta_subject.bloodresultslft"),
    Crf(show_order=40, model="meta_subject.bloodresultsrft"),
    Crf(show_order=50, model="meta_subject.urinedipsticktest"),
    name="9m",
)

crfs_12m = FormsCollection(
    Crf(show_order=10, model="meta_subject.bloodresultsglu"),
    Crf(show_order=20, model="meta_subject.bloodresultsfbc"),
    Crf(show_order=30, model="meta_subject.bloodresultslft"),
    Crf(show_order=40, model="meta_subject.bloodresultsrft"),
    Crf(show_order=50, model="meta_subject.urinedipsticktest"),
    Crf(show_order=60, model="meta_subject.malariarapidtest"),
    name="12m",
)
