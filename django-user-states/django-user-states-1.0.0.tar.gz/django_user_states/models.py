from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.auth.models import User, Group, Permission
from .managers import StateManager

class State(PolymorphicModel):
    name = models.CharField(max_length=30, unique=True)
    priority = models.IntegerField(unique=True)
    public = models.BooleanField()

    users = models.ManyToManyField(User, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    objects = StateManager()

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return '%s (%s%d)' % (self.name, 'Public ' if self.public else '', self.priority)
    
    def available_to_user(self, user):
        return True == self.public 
