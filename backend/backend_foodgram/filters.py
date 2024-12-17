from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import CharFilter

from .models import Tag, Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
