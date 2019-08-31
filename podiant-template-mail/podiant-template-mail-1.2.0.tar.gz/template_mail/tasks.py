from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send(
    subject, md_full, html_full, sender, recipient, attachments={}
):
    msg = EmailMultiAlternatives(
        subject,
        md_full,
        sender or settings.DEFAULT_FROM_EMAIL,
        [recipient]
    )

    msg.attach_alternative(html_full, 'text/html')

    for filename, (data, mimetype) in attachments.items():
        if callable(data):
            msg.attach(filename, data(), mimetype)
        else:
            msg.attach(filename, data, mimetype)

    msg.send()
