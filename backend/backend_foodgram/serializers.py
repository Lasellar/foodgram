import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    ModelSerializer, ImageField, IntegerField, PrimaryKeyRelatedField
)

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag, Favorite
)
from ..users.serializers import UserSerializer

User = get_user_model()


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
        fields = ('name', 'measurement_unit', 'amount')


class IngredientGETSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeCreateSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(
                name=ingredient_data['name'],
                measurement_unit=ingredient_data['measurement_unit'],
                amount=ingredient_data['amount']
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient
            )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(
                name=ingredient_data['name'],
                measurement_unit=ingredient_data['measurement_unit'],
                amount=ingredient_data['amount']
            )
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=ingredient
            )
        return instance


class RecipeShippingCartSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeGETSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    image = Base64ImageField(required=False)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_fovorited',
            'name', 'image', 'text', 'cooking_time'
        )
