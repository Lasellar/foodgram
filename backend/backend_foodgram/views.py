from django.shortcuts import render
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin
)
from rest_framework.permissions import IsAdminUser

from .models import (
    Tag, Ingredient,
)
from .serializers import (
    TagSerializer, IngredientSerializer
)


class TagViewSet(RetrieveModelMixin, ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)


class IngredientViewSet(RetrieveModelMixin, ListModelMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser,)
