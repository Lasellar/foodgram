from django.http import FileResponse
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import (
    ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
)
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin
)
from rest_framework.permissions import IsAdminUser

from .filters import IngredientFilter
from .models import (
    Tag, Ingredient, Recipe, ShoppingCart, Favorite
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeCreateSerializer,
    IngredientGETSerializer, RecipeGETSerializer, ShoppingCartSerializer,
    FavoriteSerializer
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGETSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user.id
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user, 'recipe': recipe.id},
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user.id
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': user, 'recipe': recipe.id},
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                    user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)



















