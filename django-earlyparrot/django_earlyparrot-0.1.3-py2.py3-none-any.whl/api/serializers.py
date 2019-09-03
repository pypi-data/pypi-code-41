from rest_framework import serializers

from ..models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    campaignId = serializers.CharField(source='campaign_id')

    class Meta:
        model = Campaign
        fields = ['name', 'campaignId']
