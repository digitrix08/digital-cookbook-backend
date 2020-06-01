from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipe.models import Recipe, Tag, Ingredient
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **kwargs):
    defaults = {
        'name': 'Omlette',
        'price': 30.00,
        'time': 5
    }
    defaults.update(kwargs)
    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, name="Non-veg"):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Egg"):
    return Ingredient.objects.create(user=user, name=name)


def get_detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


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

    def test_recipe_detail_view(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = get_detail_url(recipe.id)
        response = self.client.get(url)
        serialized_data = RecipeDetailSerializer(recipe).data

        self.assertEqual(response.data, serialized_data)
