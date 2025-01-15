from django.contrib.auth import get_user_model
from django_filters import FilterSet
from django_filters import (
    CharFilter, MultipleChoiceFilter, BooleanFilter, NumberFilter
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
    is_favorited = NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = NumberFilter(method='get_is_in_shopping_cart')
    tags = CharFilter(
        field_name='tags__slug', lookup_expr='exact', method='filter_by_tags'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

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

    def filter_by_tags(self, queryset, name, value):
        return queryset.filter(tags__slug=value)







