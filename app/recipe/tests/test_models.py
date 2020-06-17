from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from recipe.models import Tag, Ingredient, Recipe
from recipe.utils.recipe import get_image_path


class TestRecipes(TestCase):

    def setUp(self) -> None:
        self.test_user = get_user_model().objects.create_user(
            email="test_user@test.com",
            password="testpassword123",
            name="test_name"
        )

    def test_tag_str(self):
        """Testing tag model"""
        tag = Tag.objects.create(
            user=self.test_user,
            name="Non-Veg"
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Testing Ingredient models"""
        ingredient = Ingredient.objects.create(
            name='milk',
            user=self.test_user
        )

        self.assertEqual(ingredient.name, str(ingredient))

    def test_recipe_str(self):
        """Testing recipe model"""
        recipe = Recipe.objects.create(
            name="omlete",
            time=5,
            price=30,
            user=self.test_user
        )

        self.assertEqual(recipe.name, str(recipe))

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test image location and path """
        test_uuid = 'test_uuid'
        mock_uuid.return_value = test_uuid

        file_path = get_image_path(None, image_name="test_image.jpg")
        expected_path = f'uploads/recipes/{test_uuid}.jpg'

        self.assertEqual(file_path, expected_path)
