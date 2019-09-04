import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from ...models import Campaign
from ...signals_define import referral_reward_acquired

logger = logging.getLogger('referral')


class RewardAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        status_code = status.HTTP_404_NOT_FOUND
        webhook_data = request.data

        try:
            campaign = Campaign.objects.get(campaign_id=webhook_data.get('campaignId'))
            user_from = campaign.users.get(email=webhook_data.get('email'))

            referral_reward_acquired.send(
                sender=campaign.__class__,
                user_from=user_from,
                reward_data=webhook_data,
            )
            status_code = status.HTTP_200_OK
            logger.info('RewardAPIView OK')

        except Campaign.DoesNotExist:
            logger.error('Campaign.DoesNotExist')

        except get_user_model().DoesNotExist:
            logger.error('User.DoesNotExist')

        return HttpResponse(status=status_code)
