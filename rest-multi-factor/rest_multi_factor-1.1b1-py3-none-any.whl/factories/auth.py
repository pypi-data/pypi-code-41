"""
Here is the Auth Factory defined, this factory will
generate a knox token.
"""

__all__ = ("AuthFactory",)

from factory import DjangoModelFactory, SubFactory

from rest_multi_factor.utils import get_token_model

from tests.utils import get_token_object, get_token_string
from rest_multi_factor.factories.user import UserFactory


class AuthFactory(DjangoModelFactory):
    """
    Auth Factory, generates new instances
    """
    class Meta:
        model = get_token_model()

    user = SubFactory(UserFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        created = manager.create(*args, **kwargs)

        instance = get_token_object(created)
        setattr(instance, "token", get_token_string(created))

        return instance
