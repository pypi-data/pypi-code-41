from djangoldp.views import LDPViewSet
from .models import Resource

class PendingResourcesViewSet(LDPViewSet):
  model = Resource

  def get_queryset(self, *args, **kwargs):
    return super().get_queryset(*args, **kwargs)\
          .filter(review__status='pending', language__in=self.request.user.mentor_profile.languages.all(), fields__in=self.request.user.mentor_profile.fields.all())\
          .exclude(submitter=self.request.user)