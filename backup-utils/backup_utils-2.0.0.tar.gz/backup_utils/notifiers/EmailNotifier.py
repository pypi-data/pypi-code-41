from smtplib import SMTP
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..Notifier import Notifier

from ..utils import hostname, render


class EmailNotifier(Notifier):
    """
    Send an email as Notification, use SMTP protocol.

    .. seealso:: Notifier()
    """

    def send(self, msg, attachments={}):
        """
        .. seealso:: Notifier.send()
        """
        mail = MIMEMultipart()
        subject = render(self._config.get("subject", "Panic"))
        hname = hostname()
        mail["Subject"] = subject
        mail["From"] = self._config.get("from", "backup@" + hname)
        mail["To"] = self._config.get("to", "postmaster@" + hname)

        mail.attach(MIMEText(msg))

        for name, data in attachments.items():
            part = MIMEApplication(data, Name=name)
            part["Content-Disposition"] = 'attachment; filename="{}"'.format(name)
            mail.attach(part)

        s = SMTP(
            self._config.get("host", "smtp." + hname), self._config.get("port", 587)
        )

        s.login(
            self._config.get("login", "postmaster@" + hname),
            self._config.get("pswd", ""),
        )
        s.sendmail(mail["From"], mail["To"], mail.as_string())
        s.quit()
