from django.db.models import (
    Model, CharField, SlugField, Choices
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


class Ingredient(Model):
    name = CharField(verbose_name='Ингредиент', max_length=128)
    measurement_unit = CharField(
        max_length=4, choices=MEASUREMENT_UNIT_CHOICES,
        verbose_name='Мера измерения'
    )
