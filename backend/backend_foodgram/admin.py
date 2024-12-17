from django.conf import settings
from django.contrib.admin import (
    ModelAdmin, register, TabularInline
)

from .models import Tag, Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('id', 'name', 'slug')
    list_filter = ('id', 'name', 'slug')
    empty_value_display = settings.EMPTY_VALUE


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('id', 'name', 'measurement_unit')
    list_filter = ('id', 'name')
    empty_value_display = settings.EMPTY_VALUE
