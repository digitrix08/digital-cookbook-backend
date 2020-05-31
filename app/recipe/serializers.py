from rest_framework import serializers
from .models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_Fields = ('id',)
