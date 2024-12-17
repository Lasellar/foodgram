from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin
)
from rest_framework.permissions import IsAdminUser

from .filters import IngredientFilter
from .models import (
    Tag, Ingredient, Recipe
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeCreateSerializer
)


class TagViewSet(RetrieveModelMixin, ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = None


class IngredientViewSet(RetrieveModelMixin, ListModelMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeCreateViewSet(CreateModelMixin):
    serializer_class = RecipeCreateSerializer


















