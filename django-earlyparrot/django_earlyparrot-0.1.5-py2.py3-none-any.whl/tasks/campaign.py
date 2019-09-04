import requests
import logging

from celery import Task


logger = logging.getLogger('referral')


class CampaignSubscribeTask(Task):
    ignore_result = True
    name = 'CampaignSubscribeTask'

    def run(self, *args, **kwargs):
        campaign_id = kwargs.get('campaign_id')
        url = 'https://admin.earlyparrot.com/api/campaigns/{}/subscribe'.format(campaign_id)

        logger.info('CampaignSubscribeTask: {}'.format(campaign_id))

        data = {
            'firstName': kwargs.get('firstName'),
            'lastName': kwargs.get('lastName'),
            'email': kwargs.get('email'),
            'rh': kwargs.get('rh'),
        }

        if kwargs.get('conversionName'):
            data['conversionName'] = kwargs.get('conversionName')

        try:
            requests.post(url, data=data, format='json')
        except Exception as exc:
            logger.error('CampaignSubscribeTask.Exception: {}'.format(exc))
