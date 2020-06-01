from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipe.models import Recipe
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **kwargs):
    defaults = {
        'name': 'Omlette',
        'price': 30.00,
        'time': 5
    }
    defaults.update(kwargs)
    return Recipe.objects.create(user=user, **defaults)


class TestPublicRecipeAPI(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test for authentication required for getting recipes"""
        response = self.client.get(RECIPE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateRecipeAPI(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="test_user@y.com",
            password="test_password"
        )

        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipe(self):
        """Test retrieve recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(path=RECIPE_URL)

        recipes = Recipe.objects.all().order_by('id')
        serialized_data = RecipeSerializer(recipes, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data, serialized_data)

    def test_retrieve_recipe_specific_user(self):
        """Test retrieve recipes for a specific user"""
        user = get_user_model().objects.create_user(
            email="test_user2@y.com",
            password='test_password2'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=user)

        response = self.client.get(path=RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serialized_data = RecipeSerializer(recipes, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serialized_data)
