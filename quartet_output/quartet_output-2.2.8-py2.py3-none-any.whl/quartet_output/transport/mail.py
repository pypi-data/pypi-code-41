# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 SerialLab Corp.  All rights reserved.
from urllib.parse import urlparse, parse_qsl

from django.core.mail import EmailMessage

from quartet_capture.rules import RuleContext
from quartet_output.models import EPCISOutputCriteria


class MailMixin:
    '''
    Uses default django functionality to send an email.
    Emails are sent by configuring mailto links in the
    quartet endpoint configuration and attaching to output criteria.

    Mailto endpoints require no corresponding authentication info classes
    since only one global SMTP server per QU4RTET instance can be defined
    in the settings for sending outbound messages.
    '''
    def send_email(self, data: str, rule_context: RuleContext,
                   output_criteria: EPCISOutputCriteria,
                   info_func,
                   file_extension='txt',
                   mimetype='text/plain'):
        '''
        Parses out a mailto link and sends the data parameter to the addresses
        specified in the link.

        :param data: The data to send.
        :param rule_context: The quartet capture rules.RuleContext instance
            from the currently running rule.
        :param output_criteria: The models.OutputCriteria instance from the
            current TransportStep being executed.
        :param info_func: The info logging function from the calling step
            class.
        :param file_extension: This is the file extension for the attachement
            being sent.  It is best to leave it as txt even if the "real" data is
            JSON or XML since many email filters will block those formats.
        :param mimetype: The mimetype of the attachment.  Default is text/plain.
        :return: None.
        '''
        email = self.convert_mailto_url(output_criteria.end_point.urn)
        filename = '%s.%s' % (rule_context.task_name, file_extension)
        email.attach(filename, data, mimetype=mimetype)
        email.send()

    def convert_mailto_url(self, mailto):
        mail_info = urlparse(mailto, 'mailto')
        if mail_info.query:
            query_dict = dict(parse_qsl(mail_info.query))
        else:
            query_dict = {
                'subject': 'QU4RTET Output Messaging',
                'body': 'The included attachment has been sent from '
                        'a QU4RTET system to your inbox.',
                'reply_to': 'donotreply@qu4rtet.io',
                'from_email': 'output@qu4rtet.io'
            }
        cc = None
        bcc = None
        if 'cc' in query_dict.keys():
            cc = query_dict['cc'].split(',')
        if 'bcc' in query_dict.keys():
            bcc = query_dict['bcc'].split(',')
        email = EmailMessage(
            subject=query_dict.get('subject'),
            to=mail_info.path.split(','),
            body=query_dict.get('body', None),
            cc=cc,
            bcc=bcc,
            reply_to=query_dict.get('reply-to')
        )
        return email
