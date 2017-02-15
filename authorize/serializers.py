from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    API serializer for the User model.
    """
    # Todo: add phone number validation

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone'
        )


class RegistrationSerializer(serializers.HyperlinkedModelSerializer):
    """
    API serializer for the User model.
    """
    # Todo: add phone number validation

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone',
            'password'
        )


class LoginSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for login validation.
    """
    def __init__(self, *args, **kwargs):
        """
        Remove the UniqueValidator so we won't error
        on unique while validating email.
        """
        super(LoginSerializer, self).__init__(*args, **kwargs)

        email_field = self.fields['email']
        new_validators = [validator for validator in email_field.validators
                          if not isinstance(validator, UniqueValidator)]
        email_field.validators = new_validators

    class Meta:
        model = User
        fields = (
            'email',
            'password'
        )
