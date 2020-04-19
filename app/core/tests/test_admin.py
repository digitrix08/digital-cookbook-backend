from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminTest(TestCase):

    def setUp(self) -> None:
        """Stepup for upcaoming and current test"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="test_password"
        )
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="test_password",
            name="testuser"
        )

        self.client.force_login(self.admin_user)

    def test_user_listed(self):
        """Testing if user is listed in admin panel"""
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.name)

    def test_user_update(self):
        """Testing if user details can be updated from admin panel"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.name)
        self.assertEqual(response.status_code, 200)

    def test_user_add(self):
        """Testing if add user form is accessible in admin panel"""
        url = reverse("admin:core_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
