from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet

from orionframework.media.settings import Document, Image


class ServiceMedia(object):
    """
    Service used to manage the lifecycle of the media models.
    """

    category = 0
    """
    The category in which the image is saved against
    """

    model_class = None
    """
    The underlying model class being managed by this service.
    """

    parent_class = None
    """
    The parent related class we are contributing to.
    """

    parent = None
    """
    The parent model related to the maintained images
    """

    def __init__(self, category=0, parent=None, parent_class=None, **kwargs):

        super(ServiceMedia, self).__init__(**kwargs)

        self.category = category
        self.parent = parent
        self.parent_class = parent_class

        if not self.parent_class and self.parent:
            self.parent_class = self.parent.__class__

    def __iter__(self):
        return self.filter().__iter__()

    def get_parent_type(self):

        if not hasattr(self, "_parent_type"):
            self._parent_type = ContentType.objects.get_for_model(self.parent_class)

        return self._parent_type

    def delete(self, record=None, keys=None, **kwargs):

        final_record = self._build_record(record, keys=keys, **kwargs)

        if isinstance(final_record, QuerySet):

            for model in final_record:
                model.delete()

        else:

            final_record.delete()

        return final_record

    def all(self):
        return self.model_class.objects.all()

    def filter(self, **kwargs):

        if self.category:
            kwargs["category"] = self.category

        if self.parent_class:
            kwargs["parent_type"] = self.get_parent_type()

        if self.parent and self.parent.id:
            kwargs["parent_id"] = self.parent.id

        return self.all().filter(**kwargs).indexed().select_related("created_by", "modified_by")

    def save(self, model):

        if self.category or not model.category:
            model.category = self.category

        if self.parent_class:
            model.parent_type = self.get_parent_type()

        if self.parent and self.parent.id:
            model.parent_id = self.parent.id

        model.save()


class ServiceImage(ServiceMedia):
    """
    Service used to manage the lifecycle of the Image model.
    """

    model_class = Image


class ServiceDocument(ServiceMedia):
    """
    Service used to manage the lifecycle of the Document model.
    """

    model_class = Document
