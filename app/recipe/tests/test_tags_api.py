from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from recipe.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required_for_tags(self):
        """Test that login required for retrieving tags"""

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the private available tags API"""

    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test_password'
        )

        self.user = self.client.force_authenticate(user=user)

    def retrieve_all_tags(self):
        """ Test to retrieve all tags """

        Tag.objects.create(name='vegan', user=self.user)
        Tag.objects.create(name='lactose', user=self.user)

        response = self.client.get(path=TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serilaized_data = TagSerializer(tags, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serilaized_data)

    def retrive_user_specific_tags(self):
        """Test for retrieve a user's tags"""

        user2 = get_user_model().objects.create_user(
            email='test2@test.com',
            password='test_password'
        )

        Tag.objects.create(name='vegan', user=user2)
        tag = Tag.objects.create(name='lactose', user=self.user)

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data['name'], tag.name)