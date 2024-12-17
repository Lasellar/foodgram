from django.db.models import (
    Model, CharField, SlugField, Choices, ManyToManyField, TextField,
    PositiveSmallIntegerField, ImageField, ForeignKey, CASCADE
)

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

    def __str__(self):
        return self.name


class Recipe(Model):
    name = CharField(verbose_name='Название', max_length=256)
    text = TextField(verbose_name='Описание')
    cooking_time = PositiveSmallIntegerField(
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
    recipe = ForeignKey(Recipe, on_delete=CASCADE)
    ingredient = ForeignKey(Recipe, on_delete=CASCADE)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'
