from django.db import models
from django.utils import timezone
from django.db.models import Q

class CostCenterQuerySet(models.QuerySet):

    def active(self):
        now = timezone.now()
        return self.filter(
            (Q(start_date=None) & Q(end_date=None)) |
            (Q(start_date__lte=now) and Q(end_date=None)) |
            (Q(start_date=None) and Q(end_date__gte=now)) |
            (Q(start_date__lte=now) and Q(end_date__gte=now))
        )