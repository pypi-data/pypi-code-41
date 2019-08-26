from django.db import models
from .group_membership_queryset import GroupMembershipQuerySet

class GroupMembership(models.Model):
    """
    Represents a Person wich is a Member of that Group
    """
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    group  = models.ForeignKey('Group', on_delete=models.CASCADE)

    date_joined = models.DateField('Joined', null=True, blank=True)
    date_left   = models.DateField('Left', null=True, blank=True)

    position = models.ForeignKey(
        to='Position',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    objects = GroupMembershipQuerySet.as_manager()

    def __str__(self):
        position = self.position or self.person.position
        return f'{self.person.name} is a {position} in {self.group}'
