from django.db.models import Manager, QuerySet, Q
from django.db import transaction
from functools import reduce
from polymorphic.managers import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet

class StateQuerySet(PolymorphicQuerySet):
    def available_to_user(self, user):
        return [ state for state in self.all() if state.available_to_user(user) ]
    
    def get_for_user(self, user):
        states = self.available_to_user(user)
        if states:
            return states[0]
        else:
            return None

class StateManager(PolymorphicManager):
    def get_queryset(self):
        return StateQuerySet(self.model, using=self._db)
    
    def available_to_user(self, user):
        return self.get_queryset().available_to_user(user)
    
    def get_for_user(self, user):
        return self.get_queryset().get_for_user(user)