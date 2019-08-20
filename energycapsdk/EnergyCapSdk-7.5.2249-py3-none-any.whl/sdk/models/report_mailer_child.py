# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class ReportMailerChild(Model):
    """ReportMailerChild.

    :param last_sent: The date that the report mailer was last processesd
    :type last_sent: datetime
    :param next_sent: The next time the report mailer will be processed
    :type next_sent: datetime
    :param report_batch: The report batch associated with this report mailer
    :type report_batch: ~energycap.sdk.models.ReportBatchChild
    :param report_emails_sent: Report emails successfully sent to their
     recipient
    :type report_emails_sent: list[~energycap.sdk.models.ReportEmail]
    :param report_emails_not_sent: Report emails not successfully sent to
     their recipients
    :type report_emails_not_sent: list[~energycap.sdk.models.ReportEmail]
    """

    _attribute_map = {
        'last_sent': {'key': 'lastSent', 'type': 'iso-8601'},
        'next_sent': {'key': 'nextSent', 'type': 'iso-8601'},
        'report_batch': {'key': 'reportBatch', 'type': 'ReportBatchChild'},
        'report_emails_sent': {'key': 'reportEmailsSent', 'type': '[ReportEmail]'},
        'report_emails_not_sent': {'key': 'reportEmailsNotSent', 'type': '[ReportEmail]'},
    }

    def __init__(self, last_sent=None, next_sent=None, report_batch=None, report_emails_sent=None, report_emails_not_sent=None):
        super(ReportMailerChild, self).__init__()
        self.last_sent = last_sent
        self.next_sent = next_sent
        self.report_batch = report_batch
        self.report_emails_sent = report_emails_sent
        self.report_emails_not_sent = report_emails_not_sent
