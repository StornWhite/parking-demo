from rest_framework import status
from rest_framework.test import APIRequestFactory
from factory.fuzzy import FuzzyText
from faker import Factory

from parking.libs.api import tests as api_tests
from ...models import User
from ..factories import UserFactory


fake = Factory.create()


class UserAPITestCase(
    api_tests.BaseAPITestCase,
    api_tests.AnonymousNoAccessMixin,
    api_tests.UnauthorizedForbiddenTestCase,
    api_tests.NonStaffForbiddenTestCase
):
    """
    Tests the User model endpoints.

    For the standard DRF object and list endpoints, mixins automatically
    test the following:

      + No access via any method by anonymous users.
      + No access via any method by unauthorized users.
      + No access via any method for authorized, non-staff users.

    For staff users, test successful access to all DRF object and list
    endpoints.  Test success with valid data and appropriate responses
    for invalid data.

    Test that anonymous users can register via the /register endpoint
    and that registered users can login via the login endpoint.  Test
    that authenticated users can log out via the logout endpoint.
    """
    base_url = '/api/v1/user/'
    base_queryset = User.objects.all()
    unimplemented_methods = []
    anonymous_allowed_methods = []
    reg_url = base_url + 'register/'
    reg_data = {}   # Content defined in setUp()

    def setUp(self):
        """
        Create a User table.
        :return:
        """
        for i in range(0, 5):
            UserFactory()

        self.reg_data = {
            'email': fake.email(),
            'phone': fake.phone_number(),
            'password': FuzzyText(length=20).fuzz()
        }

        # Creates test users.
        super(UserAPITestCase, self).setUp()

    def test_staff_get_list_okay(self):
        """
        Test that staff users can GET from list endpoint.
        :return:
        """
        response = self.client_staff.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_count = User.objects.all().count()
        self.assertEqual(response.data.get('count'), user_count)

    def test_staff_get_object_okay(self):
        """
        Test that staff users can GET from object endpoint.
        :return:
        """
        first_user = User.objects.first()
        object_url = '%s%d/' % (self.base_url, first_user.id)
        response = self.client_staff.get(object_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), first_user.id)

    def test_staff_post_unimplemented(self):
        """
        Test that POST method is not implemented.  (Users must be
        created via the /register endpoint.)
        """
        data = {}
        response = self.client_staff.post(self.base_url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_staff_put_create_unimplemented(self):
        """
        Test that PUT method to list endpoint is not implemented.
        """
        data = {}
        response = self.client_staff.put(self.base_url, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_staff_put_update_okay(self):
        """
        Test that staff can PUT to object endpoint with valid data.
        """
        first_user = User.objects.first()
        object_url = '%s%d/' % (self.base_url, first_user.id)
        data = {
            'id': first_user.id,
            'email': 'somethingunique@example.com',
            'phone': '1234567890'
        }
        response = self.client_staff.put(object_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('email'), data.get('email'))
        self.assertEqual(response.data.get('phone'), data.get('phone'))

    def test_staff_patch_create_unimplemented(self):
        """
        Test that PATCH to list endpoint is not implemented.
        """
        data = {}
        response = self.client_staff.patch(self.base_url, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_staff_patch_update_okay(self):
        """
        Test that staff can PATCH to object endpoint with valid data.
        """
        first_user = User.objects.first()
        object_url = '%s%d/' % (self.base_url, first_user.id)
        data = {
            'id': first_user.id,
            'email': 'somethingunique@example.com',
            'phone': '1234567890'
        }
        response = self.client_staff.patch(object_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('email'), data.get('email'))
        self.assertEqual(response.data.get('phone'), data.get('phone'))

    def test_staff_delete_object_okay(self):
        """
        Test that staff can DELETE to object endpoint.
        """
        first_user = User.objects.first()
        object_url = '%s%d/' % (self.base_url, first_user.id)
        response = self.client_staff.delete(object_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_staff_delete_list_unimplemented(self):
        """
        Test that DELETE to list endpoint is unimplemented.
        """
        response = self.client_staff.delete(self.base_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_register_okay(self):
        """
        Test successful registration with valid data.
        """
        response = self.client_anon.post(self.reg_url, self.reg_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('email'), self.reg_data['email'])
        self.assertEqual(response.data.get('phone'), self.reg_data['phone'])

        # Endpoint should not return password!
        self.assertEqual(response.data.get('password'), None)

        # User should be logged in.
        user = User.objects.get(email=self.reg_data['email'])
        self.assertTrue(user.is_authenticated)

    def test_register_duplicate_email(self):
        """
        Test Bad Request response for duplicate email address.
        """
        first_user = User.objects.first()
        self.reg_data['email'] = first_user.email

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_bad_email(self):
        """
        Test Bad Request response for improper email address.
        """
        first_user = User.objects.first()
        self.reg_data['email'] = 'thisisnotavalidemailaddress'

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_too_long(self):
        """
        Test Bad Request response for email address too long. (254 char max)
        """
        email = FuzzyText(length=244).fuzz() + '@example.com'
        self.reg_data['email'] = email

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_no_email(self):
        """
        Test bad request response for no email address.
        """
        self.reg_data.pop('email')

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_no_phone(self):
        """
        Test bad request response for no phone.
        """
        self.reg_data.pop('phone')

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_phone_too_short(self):
        """
        Test bad request response for phone under 10 characters.
        """
        self.reg_data['phone'] = '555-1212'

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_phone_too_long(self):
        """
        Test bad request response for phone over 20 characters.
        """
        self.reg_data['phone'] = '555-1212'

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_too_short(self):
        """
        Test bad request response for password under 8 characters.
        """
        self.reg_data['password'] = 'x4j&iw'

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_too_common(self):
        """
        Test bad request response for password too common.
        """
        self.reg_data['password'] = 'password'

        response = self.client_anon.post(self.reg_url, self.reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_and_login(self):
        """
        Test that authorized users can log out and in.
        """
        logout_url = self.base_url + 'logout/'

        response = self.client_auth.get(logout_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        login_url = self.base_url + 'login/'
        login_data = {
            'email': self.user_auth.email,
            'password': 'pa55word'      # See setUp()
        }

        response = self.client_auth.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)