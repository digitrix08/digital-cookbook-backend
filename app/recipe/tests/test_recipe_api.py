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
        """Testing recipe deatil view"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = get_detail_url(recipe.id)
        response = self.client.get(url)
        serialized_data = RecipeDetailSerializer(recipe).data

        self.assertEqual(response.data, serialized_data)

    def test_create_recipe(self):
        """Testing create recipes"""
        data = {
            'name': 'Aloo Jeera',
            'price': 150.00,
            'time': 20
        }

        response = self.client.post(RECIPE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        for key in data.keys():
            self.assertEqual(data[key], getattr(recipe, key))

    def test_create_recipe_tags(self):
        """Test creating recipes with tags """
        tag1 = sample_tag(user=self.user, name='Non-Veg')
        tag2 = sample_tag(user=self.user, name='Main course')

        data = {
            'name': 'Chicken Curry',
            'price': 200.00,
            'time': 40,
            'tags': [tag1.id, tag2.id]
        }

        response = self.client.post(RECIPE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()

        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertEqual(tags.count(), 2)

    def test_create_recipe_ingredients(self):
        """Test creating recipes with ingredients """
        ingredient1 = sample_ingredient(user=self.user, name='Eggs')
        ingredient2 = sample_ingredient(user=self.user, name='Cheese')

        data = {
            'name': 'Cheese cake',
            'price': 250.00,
            'time': 50,
            'ingredients': [ingredient1.id, ingredient2.id]
        }

        response = self.client.post(RECIPE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_update_recipe_partial(self):
        """Test updating the recipe with patch request"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        new_tag = sample_tag(user=self.user, name="Eggy")

        data_to_be_updated = {
            'name': 'Cheese Omlette',
            'tags': [new_tag.id]
        }

        url = get_detail_url(recipe.id)
        self.client.patch(url, data_to_be_updated)

        recipe.refresh_from_db()

        self.assertEqual(recipe.name, data_to_be_updated['name'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_update_recipe_complete(self):
        """Test updating the recipe with put request"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        data_to_be_updated = {
            'name': 'Cheese Omlette',
            'time': 10,
            'price': 50.00
        }

        url = get_detail_url(recipe.id)
        self.client.put(url, data_to_be_updated)

        recipe.refresh_from_db()

        self.assertEqual(recipe.name, data_to_be_updated['name'])
        self.assertEqual(recipe.price, data_to_be_updated['price'])
        self.assertEqual(recipe.time, data_to_be_updated['time'])

        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 0)
