from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    ModelSerializer, ImageField, IntegerField, PrimaryKeyRelatedField,
    CharField, Serializer, SerializerMethodField, ValidationError,
    FloatField
)
from djoser.serializers import UserCreateSerializer, UserSerializer

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient,
    Favorite, ShoppingCart
)
from users.models import Subscription

import base64

User = get_user_model()


class Base64ImageField(ImageField):
    """
    Полу для хранения изображений в формате base64.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            fmt, imgstr = data.split(';base64,')
            ext = fmt.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Сериализатор для получения информации о теге."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(ModelSerializer):
    """Сериализатор для получения информации об ингредиенте."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientGETSerializer(ModelSerializer):
    """Сериализатор для получения информации об ингредиенте."""
    id = IntegerField(source='ingredient.id', read_only=True)
    name = CharField(source='ingredient.name', read_only=True)
    measurement_unit = CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    amount = FloatField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPOSTSerializer(Serializer):
    """Сериализатор для добавления ингредиента в рецепт."""
    id = IntegerField()
    amount = FloatField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'recipe', 'amount')


class RecipeCreateSerializer(ModelSerializer):
    """Сериализатор для создания рецепта."""
    ingredients = IngredientPOSTSerializer(
        many=True, source='recipeingredients'
    )
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        ingredients_list = []
        for ingredient in ingredients_data:
            ingredients_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient.get('id')
                    ),
                    amount=ingredient.get('amount')
                )
            )
        RecipeIngredient.objects.bulk_create(ingredients_list)

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.pop('image', instance.image)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipeingredients.all().delete()
            ingredients_list = [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient.get('id')
                    ),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients_data
            ]
            RecipeIngredient.objects.bulk_create(ingredients_list)
        return instance


class RecipeShortSerializer(ModelSerializer):
    """Сериализатор для получения краткой информации о рецепте."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(ModelSerializer):
    """Сериализатор для получения информации о списке покупок."""
    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe, context={'request': request}
        ).data


class FavoriteSerializer(ModelSerializer):
    """Сериализатор для получения информации об избранных рецептах."""
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe, context={'request': request}
        ).data


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации."""
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserGETSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователе."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )


class UserSubscribeRepresentSerializer(UserGETSerializer):
    """Сериализатор для получения информации о подписках пользователя."""
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )
        read_only_fields = (
            'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes_limit = int(
            recipes_limit
        ) if recipes_limit is not None else None
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:recipes_limit]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return len(obj.recipes.all())


class UserSubscribeSerializer(ModelSerializer):
    """Сериализатор для подписки на пользователя."""
    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, data):
        if data['user'] == data['author']:
            raise ValidationError('Ошибка подписки.')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        author = instance.author
        return UserSubscribeRepresentSerializer(
            author, context={'request': request}
        ).data


class RecipeGETSerializer(ModelSerializer):
    """Сериализатор для получения информации о рецепте."""
    ingredients = IngredientGETSerializer(
        many=True, source='recipeingredients'
    )
    tags = TagSerializer(many=True, read_only=True)
    author = UserGETSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.id
        return Favorite.objects.filter(
            user=user_id, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            user=user_id, recipe=obj
        ).exists()
