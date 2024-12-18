from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (
    Model, CharField, SlugField, Choices, ManyToManyField, TextField,
    IntegerField, ImageField, ForeignKey, CASCADE, UniqueConstraint
)

User = get_user_model()

MEASUREMENT_UNIT_CHOICES = (
    ('kg', 'кг'),
    ('g', 'г'),
    ('mg', 'мг'),
    ('l', 'л'),
    ('ml', 'мл')
)


class Tag(Model):
    name = CharField(verbose_name='Название', max_length=16)
    slug = SlugField(verbose_name='Слаг', max_length=32)

    def __str__(self):
        return self.name


class Ingredient(Model):
    name = CharField(verbose_name='Ингредиент', max_length=128)
    measurement_unit = CharField(
        max_length=4, choices=MEASUREMENT_UNIT_CHOICES,
        verbose_name='Мера измерения'
    )
    amount = IntegerField()

    def __str__(self):
        return self.name


class Recipe(Model):
    name = CharField(verbose_name='Название', max_length=256)
    text = TextField(verbose_name='Описание')
    cooking_time = IntegerField(
        verbose_name='Время приготовления(в минутах)'
    )
    tags = ManyToManyField(Tag, through='RecipeTag')
    ingredients = ManyToManyField(Ingredient, through='RecipeIngredient')
    image = ImageField(upload_to='recipes/images/')

    def __str__(self):
        return self.name


class RecipeTag(Model):
    recipe = ForeignKey(Recipe, on_delete=CASCADE)
    tag = ForeignKey(Tag, on_delete=CASCADE)

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE, related_name='recipeingredients'
    )
    ingredient = ForeignKey(
        Ingredient, on_delete=CASCADE, related_name='recipeingredients'
    )

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorite(Model):
    user = ForeignKey(
        User, on_delete=CASCADE, related_name='favorites'
    )
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE, related_name='favorites'
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}'


class ShoppingCart(Model):
    user = ForeignKey(
        User, on_delete=CASCADE, related_name='shopping_carts'
    )
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE, related_name='shopping_carts'
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_carts_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у {self.user.username}'
