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

    def test_email_normalization_test(self):
        """ Testing email normalization """
        email = "test123@TEST.COM"
        password = "test_password"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_create_user_with_invalid_email(self):
        """ Testing crate user with in valid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password="test123"
            )

    def test_create_super_user(self):
        """ Testing for creating a super user"""
        email = "test123@TEST.COM"
        password = "test_password"

        super_user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertEqual(super_user.email, email.lower())
        self.assertTrue(super_user.check_password(raw_password=password))
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_staff)
