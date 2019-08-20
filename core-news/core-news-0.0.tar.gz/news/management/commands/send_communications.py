import datetime, os

from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from news.models import Message, MailingList, Communication
from django.template import Template, Context



class Command(BaseCommand):
    help = 'Command to send the communications.'


    def __select_mailing_lists(self, when=None):

        when  = timezone.now() if when is None else when
        lists = MailingList.objects.all()

        return lists


    def handle(self,  *args, **options):

        mailing_lists = self.__select_mailing_lists()

        for lst in mailing_lists:

            msgs = lst.get_messages()

            t = Template(lst.template.code)
            c = Context({"messages": msgs})

            email_subject = lst.subject
            email_body = t.render(c)

            com = Communication(
                name=email_subject,
                html=email_body,
                sent_on=timezone.now(),
                sent_to=lst,
                messages=msgs
            )
            com.save()