from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipe.models import Ingredient, Recipe
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

    def test_ingredient_create(self):
        """Test creating an ingredient"""
        data = {'name': "new ingredient"}
        response = self.client.post(
            path=INGREDIENT_URL,
            data=data
        )

        ingredient_exists = Ingredient.objects.filter(name=data['name']
                                                      ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ingredient_exists)

    def test_ingredient_create_invalid(self):
        """Test creating an ingredient when the data is invalid"""
        data = {'name': ""}
        response = self.client.post(
            path=INGREDIENT_URL,
            data=data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Bread'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Egg'
        )
        recipe1 = Recipe.objects.create(
            name="Cheese Toast",
            time=5,
            price=30
        )
        recipe1.ingredeints.add(ingredient1)

        response = self.client.get(
            path=INGREDIENT_URL,
            data={'assigned_only': 1}
        )

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Egg'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Milk'
        )
        recipe1 = Recipe.objects.create(
            name="Egg Toast",
            time=5,
            price=30
        )
        recipe2 = Recipe.objects.create(
            name="Egg pockets with meat",
            time=5,
            price=30
        )

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient1)

        response = self.client.get(
            path=INGREDIENT_URL,
            data={'assigned_only': 1}
        )

        self.assertEqual(len(response.data), 1)
