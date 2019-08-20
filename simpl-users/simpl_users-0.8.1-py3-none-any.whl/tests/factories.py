import factory


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    first_name = factory.Sequence(lambda n: 'Test #{0}'.format(n))
    last_name = 'User'
    password = factory.PostGenerationMethodCall('set_password', 'password')

    class Meta:
        model = 'simpl_users.User'
        django_get_or_create = ('email', )
