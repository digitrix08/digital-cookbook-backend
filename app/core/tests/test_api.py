from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('core:create')
TOKEN_CREATE_URL = reverse('core:token')
USER_PROFILE_URL = reverse('core:profile')


def create_user(**kwargs):
    """
    Create user with kwargs provided
    :return: User
    """
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self):
        """
         Test creating using with a valid data is successful
        """
        user_data = {
            "email": "testemail@test.com",
            "password": "test_password",
            "name": "test_user_pa"
        }

        response = self.client.post(CREATE_USER_URL, user_data)
        user = get_user_model().objects.get(**response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            user.check_password(raw_password=user_data["password"])
        )
        self.assertNotIn("password", response.data)

    def test_user_already_exist(self):
        """
        Test creating a user that already exists fails
        """
        user_data = {
            "email": "testemail@test.com",
            "password": "test_password",
            "name": "test_user_pa"
        }
        create_user(**user_data)
        response = self.client.post(CREATE_USER_URL, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        user_data = {
            "email": "testemail@test.com",
            "password": "tpa",
            "name": "paweqwq"
        }
        response = self.client.post(CREATE_USER_URL, user_data)
        user_exists = get_user_model().objects.filter(
            email=user_data["email"]
        ).exists()

        self.assertFalse(user_exists)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_auth_token_success(self):
        """
        Testing auth token generation for a user
        """
        user_data = {
            "email": "testemail@test.com",
            "password": "test_password",
        }
        create_user(**user_data)

        response = self.client.post(TOKEN_CREATE_URL, user_data)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_auth_token_with_wrong_credentials(self):
        """
        Testing auth token generation with wrong credentials
        """
        test_data = {
            "email": "testemail@test.com",
            "password": "wrong_password",
        }
        create_user(**{
            "email": "testemail@test.com",
            "password": "test_password",
        })

        response = self.client.post(TOKEN_CREATE_URL, test_data)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_auth_token_user_does_not_exist(self):
        """
        Testing auth token generation when user does not exist
        """
        test_data = {
            "email": "testemail@test.com",
            "password": "test_password",
        }

        response = self.client.post(TOKEN_CREATE_URL, test_data)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_auth_token_with_missing_credentials(self):
        """
        Testing auth token generation with missing credentials
        """
        test_data = {
            "email": "testemail@test.com",
            "password": "",
        }

        response = self.client.post(TOKEN_CREATE_URL, test_data)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_profile_unauthorized(self):
        """Test to retrieve user profile for unauthorised user """
        test_data = {
            "email": "testemail@test.com",
            "password": "test_password",
        }

        response = self.client.get(USER_PROFILE_URL, test_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.test_user = create_user(**{
            "email": "testemail@test.com",
            "password": "test_password",
            "name": "test_user_pa"
        })

        self.client.force_authenticate(user=self.test_user)

    def test_retrieve_user_profile(self):
        """Test for retrieving user profile for test"""
        response = self.client.get(USER_PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "email": self.test_user.email,
            "name": self.test_user.name
        })

    def test_post_method_not_allowed(self):
        """Testing post method is not allowed in user profile"""
        response = self.client.post(USER_PROFILE_URL, {})
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        """Test updating the user profile"""
        updated_data = {
            "name": "new_name",
            "password": "updated_password"
        }
        response = self.client.patch(USER_PROFILE_URL, updated_data)

        self.test_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_data['name'], self.test_user.name)
        self.assertTrue(
            self.test_user.check_password(updated_data["password"])
        )
