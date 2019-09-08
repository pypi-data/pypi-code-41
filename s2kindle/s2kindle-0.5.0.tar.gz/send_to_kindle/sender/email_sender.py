import smtplib
from email.encoders import encode_base64
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.utils import getaddresses


class EmailSender:

    # pylint: disable=too-many-locals,too-many-arguments
    def __init__(self, from_email, password, host, port, use_tls):
        self.from_email = from_email
        self.password = password
        self.port = port
        self.host = host
        self.use_tls = use_tls

    def prepare_attachment(self, attachment_path):
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(open(attachment_path, "rb").read())
        encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition", f'attachment; filename="{attachment_path.name}"'
        )
        return attachment

    def prepare_message(self, subject, recipients):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["To"] = recipients
        msg["From"] = self.from_email
        return msg

    def get_addresses(self, to_email):
        return [addr[1] for addr in getaddresses([to_email]) if addr[1]]

    def send_mail(self, subject, to_email, attachment_path):
        recipients = self.get_addresses(to_email)
        msg = self.prepare_message(subject, recipients)
        part = self.prepare_attachment(attachment_path)
        msg.attach(part)
        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.from_email, self.password)
            server.sendmail(self.from_email, recipients, msg.as_string())
