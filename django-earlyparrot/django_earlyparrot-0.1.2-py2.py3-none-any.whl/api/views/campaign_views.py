from django.conf import settings

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from ...models import Campaign
from ..serializers import CampaignSerializer


class CampaignViewSet(ListAPIView):

    model = Campaign
    queryset = Campaign.objects.filter(status=settings.REFERRAL_CAMPAIGN_STATUS_ACTIVE)
    permission_classes = (IsAuthenticated, )
    serializer_class = CampaignSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(users__email=self.request.user.email)
