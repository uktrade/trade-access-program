import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    email = factory.Sequence(lambda n: 'user-{0}@test.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True
    is_staff = False
    is_superuser = False
