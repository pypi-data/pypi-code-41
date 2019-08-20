from django.contrib.contenttypes.models import ContentType
from django.db import models


class PermissionQuerySet(models.QuerySet):

    def filter_by_auth_permissions(self, user, model, codenames):
        """Auxiliary method that inspects the RankedPermissions table
        to check if the user belongs to a group with the required permissions.

        Returns a RankedPermissions queryset.
        """

        contenttype = ContentType.objects.get_for_model(model)

        for i, codename in enumerate(codenames):
            if codename in ['add', 'view', 'change', 'delete']:
                codenames[i] = f'{codename}_{contenttype.model}'

        # print('REQUIRED PERMISSIONS:', required_permissions)

        # print('USER SUMMARY')
        # for g in user.groups.all():
        #     print(g.name)
        #     for p in g.permissions.all():
        #         print('\t', p.codename)

        # Search for the user auth groups with necessary permissions
        auth_groups = user.groups.filter(
            permissions__codename__in=codenames,
            permissions__content_type=contenttype,
        )

        return self.filter(djangogroup__in=auth_groups)
