from django.contrib.auth import get_user_model
from django.db.models import (
    Model, CharField, SlugField, ManyToManyField, TextField,
    IntegerField, ImageField, ForeignKey, CASCADE, UniqueConstraint,
    FloatField
)

User = get_user_model()


class Tag(Model):
    """
    Модель тега.
    """
    name = CharField(verbose_name='Название', max_length=16, unique=True)
    slug = SlugField(verbose_name='Слаг', max_length=32, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(Model):
    """
    Модель ингредиента.
    """
    name = CharField(verbose_name='Ингредиент', max_length=1024)
    measurement_unit = CharField(
        max_length=64,
        verbose_name='Мера измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(Model):
    """
    Модель рецепта.
    """
    author = ForeignKey(
        User, on_delete=CASCADE, related_name='recipes'
    )
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeTag(Model):
    """
    Модель для связи рецептов и тегов.
    """
    recipe = ForeignKey(Recipe, on_delete=CASCADE)
    tag = ForeignKey(Tag, on_delete=CASCADE)

    def __str__(self):
        return f'{self.recipe} - {self.tag}'

    class Meta:
        verbose_name = 'Рецепт-Тег'
        verbose_name_plural = 'Рецепты-Теги'


class RecipeIngredient(Model):
    """
    Модель для связи рецептов и ингредиентов.
    """
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE, related_name='recipeingredients'
    )
    ingredient = ForeignKey(
        Ingredient, on_delete=CASCADE, related_name='recipeingredients'
    )
    amount = FloatField()

    class Meta:
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient', 'amount'),
                name='unique_recipeingredient_recipe_ingredient_amount'
            )
        ]
        verbose_name = 'Рецепт-Ингредиент'
        verbose_name_plural = 'Рецепты-Ингредиенты'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorite(Model):
    """
    Модель для связи пользователя с его избранными рецептами.
    """
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
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}'


class ShoppingCart(Model):
    """
    Модель для связи пользователя с его рецептами в корзине покупок.
    """
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
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у {self.user.username}'


class RecipeShortLink(Model):
    """
    Модель для связи рецептов с их короткими ссылками.
    """
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE, related_name='fullrecipe'
    )
    short_link = CharField(max_length=4, unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'short_link'),
                name='unique_recipeshortlink_recipe_shortlink'
            ),
        ]
        verbose_name = 'Рецепт-Короткая ссылка'
        verbose_name_plural = 'Рецепты-Короткие ссылки'
