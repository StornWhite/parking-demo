import django.db.models as db_models
import django.contrib.auth.models as auth_models


class UserManager(auth_models.BaseUserManager):
    """
    Custom UserManager is needed to substitute email for username
    as User's identifier.
    """
    use_in_migrations = True

    def _create_user(
            self, email, phone, password, **extra_fields
    ):
        """
        Creates a User with email as User's identifier and requires
        first_name and last_name.

        :param email: string in valid email format
        :param phone: string
        :param password: string
        :param extra_fields: dictionary of additional User model fields
        :return: User object
        """
        # Lowercases email domain.
        email = self.normalize_email(email).strip()

        # Create and save user object.
        user = self.model(
            email=email,
            phone=phone.strip(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(
        self, email, phone, password, **extra_fields
    ):
        """
        See _create_user() docstring.
        Creates normal non-staff, non-superuser user.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self._create_user(
            email, phone, password, **extra_fields
        )

        return user

    def create_superuser(
            self, email, phone, password, **extra_fields
    ):
        """
        See _create_user docstring.
        User with staff and superuser status.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user = self._create_user(
            email, phone, password, **extra_fields
        )

        return user


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    """
    User model is customized to use email address as username.
    """
    email = db_models.EmailField(unique=True)
    phone = db_models.CharField(max_length=15)
    is_active = db_models.BooleanField(default=True)
    is_staff = db_models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    # Required by AbstractBaseUser.
    def get_short_name(self):
        return self.email

    # Required by AbstractBaseUser.
    def get_full_name(self):
        return self.email
