from collections import Iterable
from random import shuffle
from datetime import datetime

from django.db.models import Manager
from .statuses import Statuses


class BasePublicationManager(Manager):
    def get_published(self):
        return self.filter(
            is_hidden=False, status=Statuses.PUBLISHED.name,
            publication_date__lte=datetime.now()
        )

    def get_random(self, exclude_ids=None, category_slug=None, limit=3):
        query = self.get_published()

        if exclude_ids and isinstance(exclude_ids, Iterable):
            query = query.exclude(id=exclude_ids) if isinstance(exclude_ids, str) else query.exclude(id__in=exclude_ids)

        id_list = [item.id for item in query]
        shuffle(id_list)

        return self.filter(id__in=id_list[:limit])
