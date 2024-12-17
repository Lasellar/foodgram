import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import (
    ModelSerializer, ImageField
)

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag
)


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            fmt, imgstr = data.split(';base64,')
            ext = fmt.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeCreateSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=current_ingredient
            )
        for tag in tags:
            current_tag, status = Tag.objects.get_or_create(**tag)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        return recipe

