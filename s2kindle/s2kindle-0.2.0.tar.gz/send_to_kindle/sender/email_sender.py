import smtplib
from email.encoders import encode_base64
from email.mime.multipart import MIMEBase, MIMEMultipart


class EmailSender:
    def __init__(self, from_email, password, host, port):
        self.from_email = from_email
        self.password = password
        self.port = port
        self.host = host

    def prepare_attachment(self, attachment_path):
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(open(attachment_path, "rb").read())
        encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition", f'attachment; filename="{attachment_path.name}"'
        )
        return attachment

    def prepare_message(self, subject, to_email):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["To"] = to_email
        msg["From"] = self.from_email
        return msg

    def send_mail(self, subject, to_email, attachment_path):
        msg = self.prepare_message(subject, to_email)
        part = self.prepare_attachment(attachment_path)
        msg.attach(part)
        with smtplib.SMTP(self.host, self.port) as server:
            server.login(self.from_email, self.password)
            server.sendmail(self.from_email, to_email, msg.as_string())
