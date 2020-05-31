from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipe.models import Ingredient
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class TestPublicIngredientApi(TestCase):
    """Testing for public ingredient api"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_ingredient_api_login(self):
        """Testing login required for accessing ingredient api"""

        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateIngredientApi(TestCase):
    """Testing for private ingredient api"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testemail@y.com",
            password="test_password"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_all_ingredients(self):
        """Testing retrieving all ingredients"""

        Ingredient.objects.create(
            user=self.user,
            name="MILK"
        )
        Ingredient.objects.create(
            user=self.user,
            name="CURD"
        )

        response = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serialized_data = IngredientSerializer(ingredients, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized_data)

    def test_retrieve_ingredient_user(self):
        """ Retrieve user specific to user"""
        user2 = get_user_model().objects.create_user(
            email="testemail2@y.com",
            password="test_password"
        )
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="MILK"
        )
        Ingredient.objects.create(
            user=user2,
            name="CURD"
        )

        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)
