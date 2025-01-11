from django.contrib.auth import get_user_model
from django_filters import FilterSet
from django_filters import (
    CharFilter, MultipleChoiceFilter, BooleanFilter
)

from .models import Tag, Ingredient, Recipe


User = get_user_model()


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """
    Класс, отвечающий за фильтрацию рецептов по параметрам запроса.
    """
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')

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





