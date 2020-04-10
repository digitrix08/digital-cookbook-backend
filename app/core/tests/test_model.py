from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):

    def test_create_user_email(self):
        """ Testing creation of user with email and password """
        email = "test123@test.com"
        password = "test_password"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normailzation_test(self):
        """ Testing email normalization """
        email = "test123@TEST.COM"
        password = "test_password"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())
