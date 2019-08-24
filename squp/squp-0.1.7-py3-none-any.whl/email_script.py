# Utility for sending emails using pre-made template to companies to ask for permission for their products on our store
# Built-in Imports
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Personal imports
from information import Info
import SystemShortcuts as SyS


# Main method used
def send_emails(company_info):
    # Set up the email client
    s = smtplib.SMTP(host=Info.EHOST, port=Info.EPORT)
    # Start it
    s.starttls()
    # Log in using the AOL account
    s.login(Info.LOGIN, Info.EPWD)
    # Set up the template file content var
    tfc = None
    # Read the template file and save the content
    with open(Info.ETEMPLATE, 'r', encoding='utf-8') as tf:
        tfc = tf.read()
    # Create the template from that content
    t = Template(tfc)
    # For each brand given as input
    for c in company_info:
        # Create the message to be send
        msg = MIMEMultipart()
        # Use the information for this brand to create the body of the message
        body = t.substitute(COMPANY_NAME=c)
        # Set the "From" address
        msg['From'] = Info.LOGIN
        # Set the "To" address
        msg['To'] = company_info[c]
        # Set the subject of the email
        msg['Subject'] = 'Online Store Item Usage'
        # Attach the body of the message
        msg.attach(MIMEText(body, 'plain'))
        # Python used Rest!
        SyS.slp(1.5)
        # Send the message (in string form) using all of the above information
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        # Python used Rest!
        SyS.slp(1.5)
        # Delete the message currently being used to reset
        del msg
    # Quit the email server
    s.quit()
    # Debugging ensure functionality
    print('Emailing is done')


class EmailSending():
    
    def __init__(self, *data):
        try:
            self.company_info = data[0]
        except:
            self.company_info = None
    
    # Main method used
    def send_emails(self, *company_info):
        # Set up the email client
        s = smtplib.SMTP(host=Info.EHOST, port=Info.EPORT)
        # Start it
        s.starttls()
        # Log in using the AOL account
        s.login(Info.LOGIN, Info.EPWD)
        # Set up the template file content var
        tfc = None
        # Read the template file and save the content
        with open(Info.ETEMPLATE, 'r', encoding='utf-8') as tf:
            tfc = tf.read()
        # Create the template from that content
        t = Template(tfc)
        # Try to set the company info from the parameters given
        try:
            self.company_info = company_info[0]
        except:
            pass
        # Ensure that there is company information
        assert self.company_info is not None
        # For each brand given as input
        for c in self.company_info:
            # Create the message to be send
            msg = MIMEMultipart()
            # Use the information for this brand to create the body of the message
            body = t.substitute(COMPANY_NAME=c,
                                DEVELOPER_NAME=Info.DEVELOPER_NAME,
                                DEVELOPER_POSITION=Info.DEVELOPER_POSITION,
                                THIS_COMPANY=Info.THIS_COMPANY,
                                COMPANY_LOCATION=Info.COMPANY_LOCATION)
            # Set the "From" address
            msg['From'] = Info.LOGIN
            # Set the "To" address
            msg['To'] = self.company_info[c]
            # Set the subject of the email
            msg['Subject'] = 'Online Store Item Usage'
            # Attach the body of the message
            msg.attach(MIMEText(body, 'plain'))
            # Python used Rest!
            SyS.slp(1.5)
            # Send the message (in string form) using all of the above information
            s.sendmail(msg['From'], msg['To'], msg.as_string())
            # Python used Rest!
            SyS.slp(1.5)
            # Delete the message currently being used to reset
            del msg
        # Quit the email server
        s.quit()
        # Debugging ensure functionality
        print('Emailing is done')
