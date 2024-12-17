import base64

from rest_framework.serializers import ModelSerializer

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag
)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shoppting_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

