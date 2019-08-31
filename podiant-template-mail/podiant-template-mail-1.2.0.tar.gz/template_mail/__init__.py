from django.db import transaction
from django.template.loader import render_to_string, get_template
from django.utils.safestring import mark_safe
from markdown_deux import markdown
from mimetypes import guess_type
from .context import get_context
from .exceptions import InvalidTagError
from . import settings, tasks
import django_rq


__version__ = '1.2.0'


def send(
    recipient, subject, body_template, context,
    sender=None, tag=None, attachments={}
):
    from .models import Tag

    unsubscribe_url = None
    if tag:
        with transaction.atomic():
            if isinstance(tag, str):
                tag = {
                    'name': tag
                }

            if not tag.get('name'):
                raise InvalidTagError('Invalid email tag specified', tag)

            if Tag.objects.filter(
                recipient__iexact=recipient,
                tag=tag['name'],
                unsubscribed=True
            ).exists():
                return

            if not Tag.objects.filter(
                tag=tag['name'],
                recipient__iexact=recipient
            ).exists():
                tag = Tag.objects.create(
                    tag=tag['name'],
                    description=tag.get('description'),
                    recipient=recipient
                )
            else:
                tag = Tag.objects.get(
                    tag=tag['name'],
                    recipient=recipient
                )

            unsubscribe_url = tag.get_unsubscribe_url()

    base_context = get_context(
        recipient=recipient,
        subject=subject,
        sender=sender,
        tag=tag
    )

    md_body = render_to_string(
        body_template,
        dict(
            **base_context,
            **context
        )
    )

    mimetype, encoding = guess_type(body_template)
    if mimetype == 'text/html':
        html_body = md_body
    else:
        html_body = markdown(md_body)

    md_base = get_template('email/base.txt')
    html_base = get_template('email/base.html')

    md_full = md_base.render(
        dict(
            body=md_body,
            unsubscribe_url=unsubscribe_url,
            **base_context
        )
    )

    html_full = html_base.render(
        dict(
            body=mark_safe(html_body),
            unsubscribe_url=unsubscribe_url,
            **base_context
        )
    )

    queue = django_rq.get_queue(settings.QUEUE)
    queue.enqueue(
        tasks.send,
        args=[
            subject,
            md_full,
            html_full,
            sender,
            recipient,
            attachments
        ]
    )
