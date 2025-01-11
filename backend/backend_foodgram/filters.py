from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    CharFilter, MultipleChoiceFilter, BooleanFilter
)

from .models import Tag, Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = MultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__name'
    )
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    author = CharFilter(
        field_name='author__username'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                shopping_carts_user__user=self.request.user
            )
        return queryset





