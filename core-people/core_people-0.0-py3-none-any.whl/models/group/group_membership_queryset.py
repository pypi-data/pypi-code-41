from django.db import models
from django.utils import timezone
from django.db.models import Q

class GroupMembershipQuerySet(models.QuerySet):

    def active(self):
        """
        Filter only active people
        """
        today = timezone.localtime(timezone.now()).date()
        query = Q()
        query.add(Q(date_joined__lte=today, date_left__gte=today), Q.OR)
        query.add(Q(date_joined__lte=today, date_left=None), Q.OR)
        query.add(Q(date_joined=None, date_left__gte=today), Q.OR)
        query.add(Q(date_joined=None, date_left=None), Q.OR)
        return self.filter(query)

