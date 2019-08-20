import factory

from .models import User


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user%s' % n)
    first_name = factory.Sequence(lambda n: 'User%s Bob' % n)
    last_name = factory.Sequence(lambda n: 'User%s Smith' % n)
    email = factory.Sequence(lambda n: 'user%s@example.com' % n)

    class Meta:
        django_get_or_create = ('username', )
        model = User
