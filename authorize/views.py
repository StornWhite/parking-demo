from django.contrib.auth import login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework import status

from parking.libs.api.viewsets import NoCreateModelViewSet
from .models import User
from .serializers import UserSerializer, LoginSerializer,\
    RegistrationSerializer


class UserModelViewSet(NoCreateModelViewSet):
    """
    Full API access, except create, for Admins.
    Anonymous may POST new user registration or login.
    All may log out.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser, ]

    @list_route(methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Allows users to register for the service.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data

            try:
                validate_password(data.get('password'))
            except ValidationError as error:
                error_dict = {
                    'password': error
                }
                raise DRFValidationError(error_dict)

            user = User.objects.create_user(
                email=data.get('email'),
                password=data.get('password'),
                phone=data.get('phone')
            )
            login(request, user)
            user_serializer = UserSerializer(user)
            return Response(
                user_serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            raise DRFValidationError(serializer.errors)

    @list_route(methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        Allows registered users to log in to the service.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Look for user.
            try:
                user = User.objects.get(email=serializer.data['email'])
            except User.DoesNotExist:
                raise DRFValidationError('User does not exist.')
            # Check password.
            if user.check_password(serializer.data['password']):
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data)
            else:
                raise DRFValidationError('Password is incorrect.')
        else:
            print serializer.errors
            raise DRFValidationError(serializer.errors)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logs the user out of the service.
        """
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
