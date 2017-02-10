from rest_framework import serializers

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
            'phone',
            'password'
        )