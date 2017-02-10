from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from .models import User
from .serializers import UserSerializer


class UserModelViewSet(ModelViewSet):
    """
    Full API access for Admins.  Anonymous may POST new user data.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser, ]

    # Todo allow post for anonymous users