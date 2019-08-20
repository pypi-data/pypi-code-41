# Generated by Django 2.1.8 on 2019-04-03 08:37

import core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.AutoField(db_column='ClaimID', primary_key=True, serialize=False)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('category', models.CharField(blank=True, db_column='ClaimCategory', max_length=1, null=True)),
                ('code', models.CharField(db_column='ClaimCode', max_length=8)),
                ('date_from', core.fields.DateField(db_column='DateFrom')),
                ('date_to', core.fields.DateField(blank=True, db_column='DateTo', null=True)),
                ('status', models.SmallIntegerField(db_column='ClaimStatus')),
                ('adjustment', models.TextField(blank=True, db_column='Adjustment', null=True)),
                ('claimed', models.DecimalField(blank=True, db_column='Claimed', decimal_places=2, max_digits=18, null=True)),
                ('approved', models.DecimalField(blank=True, db_column='Approved', decimal_places=2, max_digits=18, null=True)),
                ('reinsured', models.DecimalField(blank=True, db_column='Reinsured', decimal_places=2, max_digits=18, null=True)),
                ('valuated', models.DecimalField(blank=True, db_column='Valuated', decimal_places=2, max_digits=18, null=True)),
                ('date_claimed', core.fields.DateField(db_column='DateClaimed')),
                ('date_processed', core.fields.DateField(blank=True, db_column='DateProcessed', null=True)),
                ('explanation', models.TextField(blank=True, db_column='Explanation', null=True)),
                ('feedback_status', models.SmallIntegerField(blank=True, db_column='FeedbackStatus', null=True)),
                ('review_status', models.SmallIntegerField(blank=True, db_column='ReviewStatus', null=True)),
                ('approval_status', models.SmallIntegerField(blank=True, db_column='ApprovalStatus', null=True)),
                ('rejection_reason', models.SmallIntegerField(blank=True, db_column='RejectionReason', null=True)),
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(db_column='AuditUserID')),
                ('validity_from_review', core.fields.DateTimeField(blank=True, db_column='ValidityFromReview', null=True)),
                ('validity_to_review', core.fields.DateTimeField(blank=True, db_column='ValidityToReview', null=True)),
                ('submit_stamp', core.fields.DateTimeField(blank=True, db_column='SubmitStamp', null=True)),
                ('process_stamp', core.fields.DateTimeField(blank=True, db_column='ProcessStamp', null=True)),
                ('remunerated', models.DecimalField(blank=True, db_column='Remunerated', decimal_places=2, max_digits=18, null=True)),
                ('guarantee_id', models.CharField(blank=True, db_column='GuaranteeId', max_length=50, null=True)),
                ('icd_1', models.IntegerField(blank=True, db_column='ICDID1', null=True)),
                ('icd_2', models.IntegerField(blank=True, db_column='ICDID2', null=True)),
                ('icd_3', models.IntegerField(blank=True, db_column='ICDID3', null=True)),
                ('icd_4', models.IntegerField(blank=True, db_column='ICDID4', null=True)),
                ('visit_type', models.CharField(blank=True, db_column='VisitType', max_length=1, null=True)),
                ('audit_user_id_review', models.IntegerField(blank=True, db_column='AuditUserIDReview', null=True)),
                ('audit_user_id_submit', models.IntegerField(blank=True, db_column='AuditUserIDSubmit', null=True)),
                ('audit_user_id_process', models.IntegerField(blank=True, db_column='AuditUserIDProcess', null=True)),
                ('row_id', models.BinaryField(blank=True, db_column='RowID', null=True)),
            ],
            options={
                'db_table': 'tblClaim',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ClaimAdmin',
            fields=[
                ('id', models.AutoField(db_column='ClaimAdminId', primary_key=True, serialize=False)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyId', null=True)),
                ('code', models.CharField(blank=True, db_column='ClaimAdminCode', max_length=8, null=True)),
                ('last_name', models.CharField(blank=True, db_column='LastName', max_length=100, null=True)),
                ('other_names', models.CharField(blank=True, db_column='OtherNames', max_length=100, null=True)),
                ('dob', models.DateField(blank=True, db_column='DOB', null=True)),
                ('email_id', models.CharField(blank=True, db_column='EmailId', max_length=200, null=True)),
                ('phone', models.CharField(blank=True, db_column='Phone', max_length=50, null=True)),
                ('validity_from', core.fields.DateTimeField(blank=True, db_column='ValidityFrom', null=True)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(blank=True, db_column='AuditUserId', null=True)),
                ('row_id', models.BinaryField(blank=True, db_column='RowId', null=True)),
            ],
            options={
                'db_table': 'tblClaimAdmin',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ClaimDiagnosisCode',
            fields=[
                ('id', models.AutoField(db_column='ICDID', primary_key=True, serialize=False)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('code', models.CharField(db_column='ICDCode', max_length=255)),
                ('name', models.CharField(db_column='ICDName', max_length=255)),
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(db_column='AuditUserID')),
                ('row_id', models.BinaryField(blank=True, db_column='RowID', null=True)),
            ],
            options={
                'db_table': 'tblICDCodes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ClaimItem',
            fields=[
                ('id', models.AutoField(db_column='ClaimItemID', primary_key=True, serialize=False)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('status', models.SmallIntegerField(db_column='ClaimItemStatus')),
                ('availability', models.BooleanField(db_column='Availability')),
                ('qty_provided', models.DecimalField(db_column='QtyProvided', decimal_places=2, max_digits=18)),
                ('qty_approved', models.DecimalField(blank=True, db_column='QtyApproved', decimal_places=2, max_digits=18, null=True)),
                ('price_asked', models.DecimalField(db_column='PriceAsked', decimal_places=2, max_digits=18)),
                ('price_adjusted', models.DecimalField(blank=True, db_column='PriceAdjusted', decimal_places=2, max_digits=18, null=True)),
                ('price_approved', models.DecimalField(blank=True, db_column='PriceApproved', decimal_places=2, max_digits=18, null=True)),
                ('price_valuated', models.DecimalField(blank=True, db_column='PriceValuated', decimal_places=2, max_digits=18, null=True)),
                ('explanation', models.TextField(blank=True, db_column='Explanation', null=True)),
                ('justification', models.TextField(blank=True, db_column='Justification', null=True)),
                ('rejection_reason', models.SmallIntegerField(blank=True, db_column='RejectionReason', null=True)),
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(db_column='AuditUserID')),
                ('validity_from_review', core.fields.DateTimeField(blank=True, db_column='ValidityFromReview', null=True)),
                ('validity_to_review', core.fields.DateTimeField(blank=True, db_column='ValidityToReview', null=True)),
                ('audit_user_id_review', models.IntegerField(blank=True, db_column='AuditUserIDReview', null=True)),
                ('limitation_value', models.DecimalField(blank=True, db_column='LimitationValue', decimal_places=2, max_digits=18, null=True)),
                ('limitation', models.CharField(blank=True, db_column='Limitation', max_length=1, null=True)),
                ('remunerated_amount', models.DecimalField(blank=True, db_column='RemuneratedAmount', decimal_places=2, max_digits=18, null=True)),
                ('deductable_amount', models.DecimalField(blank=True, db_column='DeductableAmount', decimal_places=2, max_digits=18, null=True)),
                ('exceed_ceiling_amount', models.DecimalField(blank=True, db_column='ExceedCeilingAmount', decimal_places=2, max_digits=18, null=True)),
                ('price_origin', models.CharField(blank=True, db_column='PriceOrigin', max_length=1, null=True)),
                ('exceed_ceiling_amount_category', models.DecimalField(blank=True, db_column='ExceedCeilingAmountCategory', decimal_places=2, max_digits=18, null=True)),
            ],
            options={
                'db_table': 'tblClaimItems',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ClaimService',
            fields=[
                ('id', models.AutoField(db_column='ClaimServiceID', primary_key=True, serialize=False)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('status', models.SmallIntegerField(db_column='ClaimServiceStatus')),
                ('qty_provided', models.DecimalField(db_column='QtyProvided', decimal_places=2, max_digits=18)),
                ('qty_approved', models.DecimalField(blank=True, db_column='QtyApproved', decimal_places=2, max_digits=18, null=True)),
                ('price_asked', models.DecimalField(db_column='PriceAsked', decimal_places=2, max_digits=18)),
                ('price_adjusted', models.DecimalField(blank=True, db_column='PriceAdjusted', decimal_places=2, max_digits=18, null=True)),
                ('price_approved', models.DecimalField(blank=True, db_column='PriceApproved', decimal_places=2, max_digits=18, null=True)),
                ('price_valuated', models.DecimalField(blank=True, db_column='PriceValuated', decimal_places=2, max_digits=18, null=True)),
                ('explanation', models.TextField(blank=True, db_column='Explanation', null=True)),
                ('justification', models.TextField(blank=True, db_column='Justification', null=True)),
                ('rejectionreason', models.SmallIntegerField(blank=True, db_column='RejectionReason', null=True)),
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(db_column='AuditUserID')),
                ('validity_from_review', core.fields.DateTimeField(blank=True, db_column='ValidityFromReview', null=True)),
                ('validity_to_review', core.fields.DateTimeField(blank=True, db_column='ValidityToReview', null=True)),
                ('audit_user_id_review', models.IntegerField(blank=True, db_column='AuditUserIDReview', null=True)),
                ('limitation_value', models.DecimalField(blank=True, db_column='LimitationValue', decimal_places=2, max_digits=18, null=True)),
                ('limitation', models.CharField(blank=True, db_column='Limitation', max_length=1, null=True)),
                ('remunerated_amount', models.DecimalField(blank=True, db_column='RemuneratedAmount', decimal_places=2, max_digits=18, null=True)),
                ('deductable_amount', models.DecimalField(blank=True, db_column='DeductableAmount', decimal_places=2, max_digits=18, null=True)),
                ('exceed_ceiling_amount', models.DecimalField(blank=True, db_column='ExceedCeilingAmount', decimal_places=2, max_digits=18, null=True)),
                ('price_origin', models.CharField(blank=True, db_column='PriceOrigin', max_length=1, null=True)),
                ('exceed_ceiling_amount_category', models.DecimalField(blank=True, db_column='ExceedCeilingAmountCategory', decimal_places=2, max_digits=18, null=True)),
            ],
            options={
                'db_table': 'tblClaimServices',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(db_column='FeedbackID', primary_key=True, serialize=False)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('care_rendered', models.BooleanField(blank=True, db_column='CareRendered', null=True)),
                ('payment_asked', models.BooleanField(blank=True, db_column='PaymentAsked', null=True)),
                ('drug_prescribed', models.BooleanField(blank=True, db_column='DrugPrescribed', null=True)),
                ('drug_received', models.BooleanField(blank=True, db_column='DrugReceived', null=True)),
                ('asessment', models.SmallIntegerField(blank=True, db_column='Asessment', null=True)),
                ('chf_officer_code', models.IntegerField(blank=True, db_column='CHFOfficerCode', null=True)),
                ('feedback_date', core.fields.DateTimeField(blank=True, db_column='FeedbackDate', null=True)),
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(db_column='AuditUserID')),
            ],
            options={
                'db_table': 'tblFeedback',
                'managed': False,
            },
        ),
    ]
