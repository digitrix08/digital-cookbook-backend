from django.test import TestCase
from django.contrib.auth import get_user_model
from recipe.models import Tag, Ingredient


class TestRecipes(TestCase):

    def setUp(self) -> None:
        self.test_user = get_user_model().objects.create_user(
            email="test_user@test.com",
            password="testpassword123",
            name="test_name"
        )

    def test_tag_str(self):
        tag = Tag.objects.create(
            user=self.test_user,
            name="Non-Veg"
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        ingredient = Ingredient.objects.create(
            name='milk',
            user=self.test_user
        )

        self.assertEqual(ingredient.name, str(ingredient))
