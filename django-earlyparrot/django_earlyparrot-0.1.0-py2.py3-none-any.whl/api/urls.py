from django.conf.urls import url

from .views import CampaignViewSet, RewardAPIView


app_name = 'referral'


urlpatterns = [
    url(r'^campaigns/$', CampaignViewSet.as_view(), name='campaign-list'),
    url(r'^webhooks/2XliDq2pdp1szRJ0LR9s2598G/$', RewardAPIView.as_view(), name='reward-awared'),
]
