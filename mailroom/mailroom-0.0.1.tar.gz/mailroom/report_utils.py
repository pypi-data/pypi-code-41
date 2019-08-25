import logging
import sys

import datetime as dt
from jinja2 import Template
import os
# import pandas as pd
# import smtplib

###################################################
# Email related imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from exchangelib import Account, Credentials, ServiceAccount, \
    HTMLBody, DELEGATE, Configuration, Message, FileAttachment

###################################################
# Setting up the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)

# Login secrets dict format
secrets_template = {
    "email_address": "",
    "password": "",
    "domain": "",
    "api_key": None
}


class Chart(object):
    '''
    '''

    def __init__(self, filename, title):
        self.filename = filename
        # instance_var1 is a instance variable
        self.title = title
        # instance_var2 is a instance variable
    xlabel = 'xlabel test'
    ylabel = 'ylabel test'

    def make_bar(data):
        plt.bar(data)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.savefig(f'{filename}.png')

        filename = f'{filename}.png'

    def make_line(data, xlabel='', ylabel=''):
        plt.plot(data)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.savefig(f'{filename}.png')

        filename = f'{filename}.png'


class Email(object):
    '''
    '''

    def __init__(self, subject="Report ", secrets=None):
        self.date = dt.date.today().strftime("%m-%d-%y")
        self.html_body = ''
        self.to_field = ''
        self.from_field = ''
        self.cc_field = ''
        self.bcc_field = ''

        if type(subject) is str:
            self.subject = subject + self.date
        else:
            raise TypeError('self.subject argument not a string')

        if secrets:
            self.secrets = secrets
        else:
            self.secrets = secrets_template

    def add_html_element(self, filepath):
        '''
        Reads .html files from a relative filepath (String) and returns the file
        '''
        if type(filepath) is str:
            absolute_filepath = os.path.join(
                os.getcwd(), 'templates', filepath)
            html_file = open(absolute_filepath, 'r')
            self.html_body += html_file.read()
            html_file.close()

            logger.info(f'{filepath} has been appended to the html body')

        else:
            raise TypeError('Function argument not a string')

    def add_image(self, filepath):
        '''
        '''
        if type(filepath) is str:
            absolute_filepath = os.path.join(
                os.getcwd(), filepath)
            # with open(absolute_filepath, 'rb') as fp:
            #     img = FileAttachment(name=absolute_filepath, content=fp.read())

            self.images.append(absolute_filepath)
            self.html_body += f'''
            <table
                align="center"
                cellspacing="0"
                cellpadding="0"
                border="0"
                width="100%">
                <tr>
                    <td align="center" widthstyle="padding: 0px 0;"><td>
                        <img
                        src="cid:{filepath}"
                        alt="image"
                        border="0"
                        display: inline;"
                    />
                    </td>
                </tr>
            </table>'''

            if self.debug:
                print(f'{filepath} image has been attached to the email')

        else:
            raise TypeError('Function argument not a string')

    def attach_images(self):
        for image in self.images:
            with open(image, 'rb') as fp:
                m.attach(FileAttachment(
                    name=image, content=fp.read(), is_inline=True, content_id=image))

    def send_smtp(self, attachment=None, server=):
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.subject
            msg['To'] = self.to_field
            msg['From'] = self.from_field

            logger.debug(print('the html_body is a ' + type(self.html_body) + ' datatype.')

            # Create the body of the message (a plain-text and an HTML version).
            # Record the MIME types of both parts - text/plain and text/html.
            # part1 = MIMEText("nothing in the plain text email", 'plain')

            part2 = MIMEText(self.html_body, 'html')
            msg.attach(part2)

            # This example assumes the image is in the current directory
            # if image == True:
            #     cwd = os.path.dirname(os.path.abspath(__file__))
            #     image_path = os.path.join(cwd, image)
            #     print(image_path)
            #     fp = open(image_path, 'rb')
            #     msgImage = MIMEImage(fp.read())
            #     fp.close()

            #     # Define the image's ID as referenced above
            #     msgImage.add_header('Content-ID', '<image1>')
            #     msg.attach(msgImage)

            try:
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()

                mail.login(self.secrets['username'], self.secrets['password'])
                mail.sendmail(self.from_address, self.from_address,
                                msg.as_string())
                mail.quit()

                logger.info(f'\n--> Email sent with subject: "{self.subject}"\n')
            except:
                logger.error('Failed to connect to gmail')
                
        def send_exchange(self, attachment=None):
            '''
            Authenticates with exchave server and sends an email
            '''
            self.connect_to_exchange()

            m = Message(
                account=self.ews_account,
                subject=self.subject,
                body=HTMLBody(self.template.render(
                    subject=self.subject, body=self.html_body)),
                to_recipients=[self.to_address],
                # defaults to sending yourself an email
                cc_recipients=[''],
                # bcc_recipients=[],
            )

            if type(attachment) is str:
                attachment_filepath = os.path.join(
                    os.getcwd(), attachment)
                with open(attachment_filepath, 'rb') as f:
                    binary_file_content = f.read()

                logger.info(f'Attaching {attachment} to the report')
                m.attach(FileAttachment(name=attachment,
                                        content=binary_file_content))

            if self.images:
                self.attach_images()

            m.send()

            logger.info(f'--> Email sent with subject: "{self.subject}"')


if __name__ == '__main__':
    pass
