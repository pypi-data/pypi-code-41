from celery import current_app as app

from .campaign import CampaignSubscribeTask

app.tasks.register(CampaignSubscribeTask())
