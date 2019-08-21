# Imports from python.
from functools import reduce
import uuid


# Imports from Django.
from django.db import models
from django.utils import timezone


# Imports from other dependencies.
from uuslug import uuslug


# Imports from civic_utils.
from civic_utils.models.managers import BaseNaturalKeyManager


class UniqueIdentifierMixin(models.Model):
    uid_base_field = "slug"
    uid_prefix = ""

    uid = models.CharField(max_length=500, editable=False, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def get_uid_prefix(self):
        return self.uid_prefix

    def get_uid_suffix(self):
        return getattr(self, self.uid_base_field)

    def generate_unique_identifier(self):
        """Generate slug and (if needed) UID field values."""
        if not self.uid:
            self.uid = "{}:{}".format(
                self.get_uid_prefix(), self.get_uid_suffix()
            )


class CommonIdentifiersMixin(UniqueIdentifierMixin):
    uid_base_field = "slug"

    uid = models.CharField(max_length=500, editable=False, blank=True)

    slug = models.SlugField(
        blank=True, max_length=255, unique=True, editable=False
    )

    class Meta:
        abstract = True

    def generate_common_identifiers(self):
        """Generate slug and (if needed) UID field values."""
        self.slug = uuslug(
            getattr(self, self.uid_base_field),
            instance=self,
            max_length=100,
            separator="-",
            start_no=2,
        )

        self.generate_unique_identifier()


class NaturalKeyMixin(models.Model):
    """A mixin to add default natural-key behaviors to Civic models.

    Borrows somewhat heavily from the following project:
    https://github.com/wq/django-natural-keys/
    """

    natural_key_fields = []

    objects = BaseNaturalKeyManager()

    class Meta:
        abstract = True

    @classmethod
    def get_natural_key_definition(cls):
        """Override for self.natural_key_fields list, if needed."""
        return cls.natural_key_fields

    @classmethod
    def get_natural_key_info(cls):
        """
        Derive natural key from first unique_together definition, noting
        which fields are related objects vs. regular fields.
        """
        fields = cls.get_natural_key_definition()
        info = []
        for name in fields:
            field = cls._meta.get_field(name)
            rel_to = None
            if hasattr(field, "rel"):
                rel_to = field.rel.to if field.rel else None
            elif hasattr(field, "remote_field"):
                if field.remote_field:
                    rel_to = field.remote_field.model
                else:
                    rel_to = None
            info.append((name, rel_to))
        return info

    @classmethod
    def get_natural_key_fields(cls):
        """
        Determine actual natural key field list, incorporating the natural keys
        of related objects as needed.
        """
        natural_key = []
        for name, rel_to in cls.get_natural_key_info():
            if not rel_to:
                natural_key.append(name)
            elif issubclass(rel_to, NaturalKeyMixin):
                nested_key = rel_to.get_natural_key_fields()
                natural_key.extend(
                    [f"{name}__{nested_name}" for nested_name in nested_key]
                )
            else:
                natural_key.append(f"{name}__pk")
        return natural_key

    def natural_key(self):
        key_field_values = [
            reduce(getattr, name.split("__"), self)
            for name in self.get_natural_key_fields()
        ]

        return key_field_values


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
