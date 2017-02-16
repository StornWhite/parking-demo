import factory
from ..models import User


class UserFactory(factory.DjangoModelFactory):
    """
    Creates a mock user object with password = 'pa55word.'
    """
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'email-%d@example.com' % n)
    phone = factory.Faker('phone_number')
    password = factory.PostGenerationMethodCall('set_password', 'pa55word')
    is_active = True
    is_staff = False
