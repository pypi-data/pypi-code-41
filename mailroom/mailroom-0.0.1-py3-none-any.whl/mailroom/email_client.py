import logging
import sys
import exchangelib
import smtplib

###################################################
# Setting up the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)
###################################################


def exchange(email_config):
    '''
        Sets up the exchangelib connection to the exchange server
        '''
    credentials = Credentials(self.email_config['username'],
                              self.email_config['password'])
    self.ews_account = Account(self.email_config['user_email_address'],
                               credentials=credentials,
                               autodiscover=True,
                               access_type=DELEGATE)

    ews_url = self.ews_account.protocol.service_endpoint
    ews_auth_type = self.ews_account.protocol.auth_type

    # if you need to impersonate, change from primary_account to alias_account
    primary_smtp_address = self.ews_account.primary_smtp_address

    config = Configuration(service_endpoint=ews_url,
                           credentials=credentials,
                           auth_type=ews_auth_type)

    a = Account(
        primary_smtp_address=primary_smtp_address,
        config=config,
        autodiscover=False,
        access_type=DELEGATE,
    )


def gmail(email_config):
    pass


def send(self, image=False):
    '''
    '''
    msg = MIMEMultipart('alternative')
    msg['Subject'] = self.subject
    msg['From'] = self.from_address
    msg['To'] = self.to_address

    # Create the body of the message (a plain-text and an HTML version).
    # Record the MIME types of both parts - text/plain and text/html.
    print(type(self.html_body))
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

    # Send the message via local SMTP server.

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()

    mail.login(username, password)
    mail.sendmail(self.from_address, self.from_address, msg.as_string())
    mail.quit()

    if self.debug:
        print(f'\n--> Email sent with subject: "{self.subject}"\n')


def send_notification(self, text, image=False):
    notification = Email(debug=True)
    notification.subject = text
    notification.send(image)
