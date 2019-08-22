from django import template
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.template import Context
from django.utils.translation import ugettext_lazy as _


class EmailTemplate(models.Model):
    """
    Email templates get stored in database so that admins can
    change emails on the fly
    
    EmailTemplate.send('expense_notification_to_admin', {
    # context object that email template will be rendered with
    'expense': expense_request,
})

  EmailTemplate.send('email_key', {
    'object':context 
},emails=('recipient@gmail.com',))

    """
    template_key = models.CharField(_('Key'),max_length=255, unique=True)

    subject = models.CharField(_('Subject'),max_length=255)
    to_email = models.CharField(_('To'),max_length=255, blank=True, null=True)
    from_email = models.CharField(_('From'),max_length=255, blank=True, null=True)
    html_template = models.TextField(_('HTML'),blank=True, null=True)
    is_html = models.BooleanField(_('Is HTML?'),default=False)

    # unique identifier of the email template

    def get_rendered_template(self, tpl, context):
        return self.get_template(tpl).render(context)

    def get_template(self, tpl):
        return template.Template(tpl)

    def get_subject(self, subject, context):
        return subject or self.get_rendered_template(self.subject, context)

    def get_body(self, body, context):
        return body or self.get_rendered_template(self._get_body(), context)

    def get_sender(self):
        return self.from_email or settings.DEFAULT_FROM_EMAIL

    def get_recipient(self, emails, context):
        return emails or [self.get_rendered_template(self.to_email, context)]

    @staticmethod
    def send(*args, **kwargs):
        EmailTemplate._send(*args, **kwargs)

    @staticmethod
    def _send(template_key, context, subject=None, body=None, sender=None,
              emails=None, bcc=None, attachments=None):
        mail_template = EmailTemplate.objects.get(template_key=template_key)
        context = Context(context)

        subject = mail_template.get_subject(subject, context)
        body = mail_template.get_body(body, context)
        sender = sender or mail_template.get_sender()
        emails = mail_template.get_recipient(emails, context)

        if not mail_template.is_html:
            return send_mail(subject, body, sender, emails, fail_silently=not
            settings.DEBUG)

        msg = EmailMultiAlternatives(subject, body, sender, emails,
                                     alternatives=((body, 'text/html'),),
                                     bcc=bcc
                                     )
        if attachments:
            for name, content, mimetype in attachments:
                msg.attach(name, content, mimetype)
        return msg.send(fail_silently=not settings.DEBUG)

    def _get_body(self):
        if not self.is_html:
            return self.plain_text

        return self.html_template

    def __str__(self):
        return "<{}> {}".format(self.template_key, self.subject)
