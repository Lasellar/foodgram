from django.conf import settings
from django.contrib.admin import (
    ModelAdmin, register, TabularInline
)

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient, Favorite,
    ShoppingCart, RecipeShortLink, RecipeTag
)


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
    search_fields = ('name',)
    list_filter = ('name', 'measurement_unit')
    empty_value_display = settings.EMPTY_VALUE


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('id', 'name', 'author', 'get_favorites_count')
    search_fields = ('author', 'name')
    list_filter = ('tags',)
    empty_value_display = settings.EMPTY_VALUE

    def get_favorites_count(self, obj):
        return obj.favorites.count()
    get_favorites_count.short_description = 'В избранном'


@register(RecipeTag)
class RecipeTagAdmin(ModelAdmin):
    list_display = ('id', 'recipe', 'tag')
    empty_value_display = settings.EMPTY_VALUE


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    empty_value_display = settings.EMPTY_VALUE


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = settings.EMPTY_VALUE


@register(ShoppingCart)
class FavoriteAdmin(ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = settings.EMPTY_VALUE


@register(RecipeShortLink)
class RecipeShortLinkAdmin(ModelAdmin):
    list_display = ('id', 'recipe', 'short_link')
    empty_value_display = settings.EMPTY_VALUE
