from django.conf import settings
from django.db import models
from django.db.models import Q

class GroupQuerySet(models.QuerySet):

    # User dependent Querysets
    # =========================================================================

    def owned_by(self, user):
        """
        Filters the Queryset to objects owned by the User or where
        he is referenced in a Foreign Key.

        This is by default what everyone sees if they have no permissions.
        """
        return self.filter(
            Q(responsible__auth_user=user)
        ).distinct()

    def managed_by(self, user, default=None):
        """
        Filters the Queryset to objects the user is allowed to manage
        given his Authorization Group profiles.

        Notes:
            RankedPermissions not used.
            `required_codenames` not used
        """

        if default is None:
            default = self.none()

        if user.is_superuser:
            return self

        if settings.PROFILE_HUMAN_RESOURCES in user.groups.all():
            # HR profile may manage all groups
            return self

        # check which groups the user is Coordinator / Admin / Manager
        research_groups = []
        for group in user.groups.all():
            parts = group.name.split(': ')
            if (
                len(parts) == 3 and
                parts[0] == 'PROFILE' and
                parts[1] in ('Group Coordinator',
                             'Group Admin',
                             'Group Manager')
            ):
                research_groups.append(parts[2])

        qs = self.filter(name__in=research_groups) or default.distinct()

        return qs

    # PyForms Querysets
    # =========================================================================

    def list_permissions(self, user):
        return self.managed_by(
            user,
            default=self.owned_by(user)
        )

    def has_add_permissions(self, user):
        return user.is_superuser

    def has_view_permissions(self, user):
        return self.list_permissions(user)

    def has_update_permissions(self, user):
        return self.list_permissions(user)

    def has_remove_permissions(self, user):
        return user.is_superuser
