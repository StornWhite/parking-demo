from rest_framework.test import APITestCase, APIClient
from rest_framework.authentication import SessionAuthentication
from rest_framework.settings import api_settings

from authorize.tests.factories import UserFactory


class BaseAPITestCase(APITestCase):
    """
    A base test case that defines authorized, unauthorized, and
    staff users during setup and which can be combined with various
    mixins to automatically perform standard test suites against
    standard Django Rest Framework behaviors.
    """
    # Override these:
    base_url = ''
    base_queryset = None
    unimplemented_methods = []
    anonymous_allowed_methods = []

    def setUp(self):
        # Factory creates mock users with password = pa55word.
        self.user_auth = UserFactory()
        self.user_unauth = UserFactory(is_active=False)
        self.user_staff = UserFactory(is_staff=True)

        # Create clients.
        self.client_anon = APIClient()

        self.client_auth = APIClient()
        self.client_auth.login(
            email=self.user_auth.email,
            password='pa55word'
        )

        self.client_unauth = APIClient()
        self.client_unauth.login(
            email=self.user_unauth.email,
            password='pa55word'
        )

        self.client_staff = APIClient()
        self.client_staff.login(
            email=self.user_staff.email,
            password='pa55word'
        )

        # Get common testing stuff.
        # Subclasses must call super().setUp *after* creating base_queryset!
        self.obj = self.base_queryset.first()
        self.list_url = self.base_url
        self.obj_url = '%s%i/' % (self.list_url, self.obj.id)
        self.obj_data = vars(self.obj)
        self.obj_data.pop('_state')

        self.unimplemented_methods = \
            [method.lower() for method in self.unimplemented_methods]

        self.unauthenticated_code = self.get_unauthenticated_code()

        self.anonymous_allowed_methods = \
            [method.lower() for method in self.anonymous_allowed_methods]

    def get_unauthenticated_code(self):
        """
        The code returned for unauthenticated users is either 403 or
        401, depending on 1st priority authentication class.
        """
        auth_classes = getattr(self, 'authentication_classes', None)
        authentication_classes = auth_classes if auth_classes \
            else api_settings.DEFAULT_AUTHENTICATION_CLASSES

        if authentication_classes[0] == SessionAuthentication:
            return 403
        else:
            return 401


class AnonymousNoAccessMixin(object):
    """
    Mixes standard tests into BaseApiTestCase for checking that
    anonymous users have no access to un-allowed methods and endpoints.
    """

    def test_anonymous_forbidden(self):
        """
        Test that anonymous users get 401 or 403 responses for methods at
        un-allowed object and list endpoints.
        """
        data = {}
        code = self.unauthenticated_code
        allowed = self.anonymous_allowed_methods

        # Get
        if 'get' in allowed:
            response = self.client_anon.get(self.obj_url)
            self.assertEqual(response.status_code, code)
            response = self.client_anon.get(self.list_url)
            self.assertEqual(response.status_code, code)

        # Post
        if 'post' in allowed:
            response = self.client_anon.post(self.list_url, data)
            self.assertEqual(response.status_code, code)

        # Put
        if 'put' in allowed:
            response = self.client_anon.put(self.obj_url, data)
            self.assertEqual(response.status_code, code)
            response = self.client_anon.put(self.list_url, data)
            self.assertEqual(response.status_code, code)

        # Patch
        if 'patch' in allowed:
            response = self.client_anon.patch(self.obj_url, data)
            self.assertEqual(response.status_code, code)
            response = self.client_anon.patch(self.list_url, data)
            self.assertEqual(response.status_code, code)

        # Delete
        if 'delete' in allowed:
            response = self.client_anon.delete(self.obj_url)
            self.assertEqual(response.status_code, code)
            response = self.client_anon.delete(self.list_url)
            self.assertEqual(response.status_code, code)


class UnauthorizedForbiddenTestCase(object):
    """
    Mixes standard tests into BaseAPITestCase for ensuring that unauthorized
    users (user.is_active = False) may not access any standard endpoints.
    """
    def test_unauthorized_forbidden(self):
        """
        Test that unauthorized users get 403 responses for all methods at
        all regular object and list endpoints.
        """
        data = {}

        # Get
        response = self.client_unauth.get(self.obj_url)
        self.assertEqual(response.status_code, 403)
        response = self.client_unauth.get(self.list_url)
        self.assertEqual(response.status_code, 403)

        # Post
        response = self.client_unauth.post(self.list_url, data)
        self.assertEqual(response.status_code, 403)

        # Put
        response = self.client_unauth.put(self.obj_url, data)
        self.assertEqual(response.status_code, 403)

        # Patch
        response = self.client_unauth.patch(self.obj_url, data)
        self.assertEqual(response.status_code, 403)
        response = self.client_unauth.patch(self.list_url, data)
        self.assertEqual(response.status_code, 403)

        # Delete
        response = self.client_unauth.delete(self.obj_url)
        self.assertEqual(response.status_code, 403)
        response = self.client_unauth.delete(self.list_url)
        self.assertEqual(response.status_code, 403)


class NonStaffForbiddenTestCase(object):
    """
    Mixes standard tests into BaseAPITestCase for ensuring that non-staff
    users (user.is_staff = False) may not access any standard endpoints.
    """
    def test_non_staff_forbidden(self):
        """
        Test that non-staff users get 403 responses for all methods at
        all regular object and list endpoints.
        """
        data = {}

        # Get
        response = self.client_auth.get(self.obj_url)
        self.assertEqual(response.status_code, 403)
        response = self.client_auth.get(self.list_url)
        self.assertEqual(response.status_code, 403)

        # Post
        response = self.client_auth.post(self.list_url, data)
        self.assertEqual(response.status_code, 403)

        # Put
        response = self.client_auth.put(self.obj_url, data)
        self.assertEqual(response.status_code, 403)

        # Patch
        response = self.client_auth.patch(self.obj_url, data)
        self.assertEqual(response.status_code, 403)
        response = self.client_auth.patch(self.list_url, data)
        self.assertEqual(response.status_code, 403)

        # Delete
        response = self.client_auth.delete(self.obj_url)
        self.assertEqual(response.status_code, 403)
        response = self.client_auth.delete(self.list_url)
        self.assertEqual(response.status_code, 403)


class AuthorizedOkayGetMixin(object):
    """
    Mixes standard tests into BaseAPITestCase for checking that authorized
    users can successfully GET to this endpoint.
    """

    def test_authorized_okay(self):
        """
        Test that authorized users successfully get data.
        """
        # Get object.
        response = self.client_auth.get(self.obj_url)
        self.assertEqual(response.status_code, 200)
        response_data = dict(response.data)

        self.assertEqual(response_data, self.obj_data)

        # Get list.
        response = self.client_auth.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        response_data = dict(response.data['results'][0])

        self.assertEqual(response_data, self.obj_data)


class AuthorizedNotImplementedMixin(object):
    """
    Mixes standard tests into BaseAPITestCase for checking that authorized
    users receive a 504 response for unimplemented methods.
    """

    def test_authorized_not_implemented(self):
        """
        Test that authorized users get 405 responses for all unimplemented
        methods at all regular object and list endpoints.
        """
        data = {}

        # Get
        if 'get' in self.unimplemented_methods:
            response = self.client_auth.patch(self.obj_url)
            self.assertEqual(response.status_code, 405)
            response = self.client_auth.patch(self.list_url)
            self.assertEqual(response.status_code, 405)

        # Post
        if 'post' in self.unimplemented_methods:
            response = self.client_auth.post(self.list_url, data)
            self.assertEqual(response.status_code, 405)

        # Put
        if 'post' in self.unimplemented_methods:
            response = self.client_auth.put(self.obj_url, data)
            self.assertEqual(response.status_code, 405)

        # Patch
        if 'post' in self.unimplemented_methods:
            response = self.client_auth.patch(self.obj_url, data)
            self.assertEqual(response.status_code, 405)
            response = self.client_auth.patch(self.list_url, data)
            self.assertEqual(response.status_code, 405)

        # Delete
        if 'post' in self.unimplemented_methods:
            response = self.client_auth.delete(self.obj_url)
            self.assertEqual(response.status_code, 405)
            response = self.client_auth.delete(self.list_url)
            self.assertEqual(response.status_code, 405)