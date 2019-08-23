from django.conf import settings
from django.db import models
from django.db.models import Q
from permissions.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class PublicationQuerySet(models.QuerySet):

    def filter_research_groups(self, groups):
        return self.filter(authors__group__in=groups)

    def filter_people(self, people):
        return self.filter(authors__in=people)

    def is_author(self, user):
        """Filters the queryset to those publications where user is author."""
        if user.is_superuser:
            return self

        assert user.person_user.count() == 1
        person = user.person_user.first()
        return self.filter(authors=person)

    def key_publications(self):
        return self.filter(publication_keypub=True)





    # PyForms Querysets
    # =========================================================================

    def __query_permissions(self, user, permissions_filter):
        # Search for the user groups with certain permissions
        contenttype = ContentType.objects.get_for_model(self.model)
        authgroups  = user.groups.filter(permissions__content_type=contenttype)
        authgroups  = authgroups.filter(permissions_filter).distinct()
        return Permission.objects.filter(djangogroup__in=authgroups)


    def __filter_by_permissions(self, user, perms):
        if user.is_superuser: return self

        if perms.exists():
            # check if the user has permissions to all publications
            if perms.filter(researchgroup=None).exists():
                return self
            else:
                if perms.exists():
                    # find which research groups the user has access to its people
                    researchgroups_withaccess = [p.researchgroup for p in perms]

                    now = timezone.now()
                    qs = self.filter(
                        Q(authors__auth_user=user) |
                        Q(
                            authors__groupmember__date_joined__lte=now,
                            authors__groupmember__date_left__gte=now,
                            authors__groupmember__group__in=researchgroups_withaccess
                        ) |
                        Q(
                            authors__groupmember__date_joined__lte=now,
                            authors__groupmember__date_left__isnull=True,
                            authors__groupmember__group__in=researchgroups_withaccess
                        ) |
                        Q(
                            authors__groupmember__date_joined__isnull=True,
                            authors__groupmember__date_left__isnull=True,
                            authors__groupmember__group__in=researchgroups_withaccess
                        )
                    )
                    return qs.distinct()

        # By default return an empty query
        return self.filter(pk=-1)




    def list_permissions(self, user):
        """
        Everyone has access to all publications
        """
        return self

    def has_view_permissions(self, user):
        """
        Everyone can see all the publications.
        """
        return True

    def has_add_permissions(self, user):
        """
        All users are allowed to add new publications.
        """
        return True

    def has_update_permissions(self, user):
        """
        Returns the queryset of objects the user can change.
        """
        if self.is_author(user).exists():
            return True

        perms = self.__query_permissions(
            user,
            Q(permissions__codename='change_publication')
        )
        return self.__filter_by_permissions(user, perms).exists()


    def has_remove_permissions(self, user):
        """
        Returns the queryset of objects the user can delete.
        """
        perms = self.__query_permissions(
            user,
            Q(permissions__codename='delete_publication')
        )
        return self.__filter_by_permissions(user, perms).exists()
