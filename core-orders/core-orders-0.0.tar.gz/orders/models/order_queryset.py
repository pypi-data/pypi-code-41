from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from permissions.models import Permission


class OrderQuerySet(models.QuerySet):

    def current_year(self):
        now = timezone.now()
        return self.filter(order_reqdate__year=now.year)

    def not_delivered(self):
        return self.filter(order_deldate=None)

    def pending_pos(self):
        qs = self.filter(order_paymethod__in=['C', 'PP'])
        return qs.filter(order_podate=None)

    # User dependent Querysets
    # =========================================================================

    def owned_by(self, user):
        """
        Filters the Queryset to objects owned by the User or where
        he is referenced in a Foreign Key.

        # TODO make a FK out of the requester_name field

        This is by default what everyone sees if they have no permissions.
        """
        return self.filter(
            Q(responsible=user)
        ).distinct()

    def managed_by(self, user, required_codenames, default=None):
        """
        Filters the Queryset to objects the user is allowed to manage
        given his Authorization Group profiles.

        Uses the RankedPermissions table.
        """

        if default is None:
            default = self.none()

        if user.is_superuser:
            return self

        ranked_permissions = Permission.objects.filter_by_auth_permissions(
            user, self.model, required_codenames)

        if ranked_permissions.exists():
            # check if the user has permissions to all objects
            if ranked_permissions.filter(researchgroup=None).exists():
                return self
            else:

                # check which groups the user has access to
                groups_withaccess = list(filter(
                    None,
                    [p.researchgroup.groupdjango for p in ranked_permissions],
                ))
                # rankings = [(p.researchgroup, p.ranking) for p in ranked_permissions]

                # If no groups are defined or if the group is linked
                # with PROFILE: Admin, give access to all groups user
                # is member of
                groups_withaccess = [g for g in groups_withaccess if g.name != settings.PROFILE_ADMIN]
                groups_withaccess = groups_withaccess or user.groups.filter(name__startswith='GROUP:')

                filters = Q()

                # Show user's orders
                filters.add(Q(responsible=user), Q.OR)

                # Show orders in user's groups
                filters.add(Q(group__in=groups_withaccess), Q.OR)

                # Show orders with expense codes in user's groups
                filters.add(Q(expensecode__financeproject__costcenter__group__in=groups_withaccess), Q.OR)

                qs = self.filter(filters).distinct()

                if 'view_personnel_orders' not in required_codenames:
                    qs = qs.exclude(expensecode__expensecode_number='01')

                return qs

        return default.distinct()

    # PyForms Querysets
    # =========================================================================

    def list_permissions(self, user):
        return self.managed_by(
            user,
            ['view', 'change'],
            default=self.owned_by(user)
        )

    def has_add_permissions(self, user):
        if user.is_superuser:
            return True

        return Permission.objects.filter_by_auth_permissions(
            user=user,
            model=self.model,
            codenames=['add'],
        ).exists()

    def has_view_permissions(self, user):
        # view_permission is useless because we let people see
        # their own objects via list_permissions
        return self.list_permissions(user)

    def has_update_permissions(self, user):
        return self.managed_by(
            user,
            ['change'],
            default=self.owned_by(user)
        ).exists()

    def has_remove_permissions(self, user):
        return self.managed_by(
            user,
            ['delete'],
            default=self.owned_by(user)
        ).exists()
