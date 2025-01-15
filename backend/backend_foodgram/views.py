from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
)
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .filters import IngredientFilter, RecipeFilter
from .models import Tag, Ingredient, Recipe, ShoppingCart, Favorite, RecipeShortLink
from users.models import Subscription

from .pagination import PageLimitAndRecipesLimitPagination
from .permissions import IsAuthenticatedAndAuthor
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeGETSerializer, ShoppingCartSerializer, FavoriteSerializer,
    UserSubscribeSerializer, UserSubscribeRepresentSerializer,
    UserGETSerializer, UserSignUpSerializer
)
from .utils import generate_short_link, generate_full_short_url, get_ingredients_list
from .validators import SignUpValidator

import base64
import random
import string

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitAndRecipesLimitPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGETSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        """
        Метод, определяющий разрешения на доступ для конкретных методов.
        """
        if (
            self.request.method == 'POST'
            or (
                self.request.method == 'DELETE'
                and
                (
                    '/favorite/' in self.request.path
                    or '/shopping_cart/' in self.request.path
                )
            )
        ):
            return (IsAuthenticated(),)
        if (
            self.request.method == 'PATCH'
            or self.request.method == 'DELETE'
        ):
            return (IsAuthenticatedAndAuthor(),)
        return super().get_permissions()

    def get_object(self):
        if '/s/' in self.request.path:
            pk = self.kwargs.get('pk')
            recipe_id = get_object_or_404(
                RecipeShortLink, short_link=pk
            ).recipe.id
            return get_object_or_404(Recipe, id=recipe_id)
        return super().get_object()

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
                    {'errors': 'Рецепта нет в избранном.'},
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

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_short_link(self, request, pk):
        recipe = Recipe.objects.filter(id=pk).exists()
        if not recipe:
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if RecipeShortLink.objects.filter(recipe=recipe).exists():
            return Response(
                generate_full_short_url(
                    RecipeShortLink.objects.get(recipe=recipe).short_link
                ),
                status=status.HTTP_200_OK
            )
        short_link = generate_short_link(request)
        while RecipeShortLink.objects.filter(short_link=short_link).exists():
            short_link = generate_short_link(request)
        recipe = Recipe.objects.get(id=pk)
        RecipeShortLink.objects.create(recipe=recipe, short_link=short_link)
        return Response(
            generate_full_short_url(short_link),
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, methods=('get',), url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        return Response(
            {'result': get_ingredients_list(request)},
            status=status.HTTP_200_OK
        )


class SignUpView(APIView, SignUpValidator):
    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionView(APIView):
    """
    Вьюсет, отвечающий за создание/удаление подписки на пользователя по id.
    """
    http_method_names = ('post', 'delete')
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        """Метод, отвечающий за создание подписки."""
        author = User.objects.filter(id=user_id)
        if not author.exists():
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, user_id):
        """Метод, отвечающий за удаление подписки."""
        user = request.user.id
        subscription = Subscription.objects.filter(user=user, author=user_id)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserSubscriptionsViewSet(ListModelMixin, GenericViewSet):
    """
    Вьюсет, отвечающий за получение списка подписок пользователя.
    """
    serializer_class = UserSubscribeRepresentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageLimitAndRecipesLimitPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class LoginView(APIView):
    """
    View-класс, отвечающий за создание/получение токена авторизации.
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User  not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({'auth_token': token.key}, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogOutView(APIView):
    """
    View-класс, отвечающий за удаление токена.
    """
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Пользователь не авторизован.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        Token.objects.get(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(ModelViewSet):
    """
    Вьюсет для работы с пользователями.
    Методы запросов и эндпоинты:

    GET:
    - users/
    - users/me/
    - users/<pk>/

    POST:
    - users/
    - users/set_password/
    - users/<pk>/subscribe/

    PUT:
    - users/me/avatar/

    DELETE:
    - users/me/avatar/
    - users/<pk>/subscribe/
    """
    queryset = User.objects.all()
    serializer_class = UserGETSerializer
    http_method_names = ('get', 'post', 'put', 'delete')

    def get_permissions(self):
        """
        Метод, определяющий разрешения на доступ для конкретных методов.
        """
        if (
            self.request.method == 'POST'
            and self.kwargs.get('pk') == 'set_password'
        ) or (
            'avatar' in self.request.path
        ):
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_object(self):
        """
        Метод, возвращающий текущего пользователя/пользователя по его id.
        Если пользователь не найден, возвращается False
        """
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        if User.objects.filter(id=self.kwargs.get('pk')).exists():
            return User.objects.get(id=self.kwargs.get('pk'))
        return False

    def list(self, request, *args, **kwargs):
        """
        Метод, отвечающий за получение списка пользователей.
        Обрабатывает GET-запросы на эндпоинт users/.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Метод, отвечающий за регистрацию пользователя.
        Обрабатывает POST-запросы на эндпоинт users/.
        """
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        Метод, отвечающий за получение профиля текущего пользователя и
        получение пользователя по его id.
        Обрабатывает GET-запросы на эндпоинты:
        users/me/
        users/<pk>/
        """
        instance = self.get_object()
        if not instance:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=('post',), url_path='set_password')
    def set_password(self, request):
        """
        Метод, отвечающий за смену пароля.
        Обрабатывает POST запросы на эндпоинт users/set_password/.
        """
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if current_password == new_password:
            return Response(
                {'detail': 'Пароли не должны совпадать.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(new_password)
        except ValidationError as exception:
            return Response(
                {'detail': exception}, status=status.HTTP_400_BAD_REQUEST
            )
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(
            {'detail': 'Введен неверный пароль.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=('put', 'delete'), url_path='me/avatar')
    def avatar(self, request):
        """
        Метод, отвечающий за добавление и удаление аватарки.
        Обрабатывает PUT и DELETE запросы на эндпоинт users/me/avatar/.
        """
        user = request.user
        if request.method == 'PUT':
            avatar = request.data.get('avatar')
            if avatar:
                if avatar.startswith('data:image/'):
                    frmt, imgstr = avatar.split(';base64,')
                    ext = frmt.split('/')[-1]
                    avatar_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'{user.username}.{ext}'
                    )
                    user.avatar.save(f'{user.username}.{ext}', avatar_file)
                    return Response(
                        {'avatar': user.avatar.url},
                        status=status.HTTP_201_CREATED)
            return Response(
                {'field_errors': ['avatar']},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'), url_path='subscribe')
    def subscribe(self, request, pk):
        """
        Метод, отвечающий за создание и удаление подписки на пользователя.
        Обрабатывает POST и DELETE запросы на эндпоинт users/<pk>/subscribe/.
        """
        user = request.user.id
        author = User.objects.filter(id=pk)
        if not author.exists():
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user, author=pk
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSubscribeSerializer(
            data={'user': user, 'author': pk},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class UserPasswordReset(APIView):
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_418_IM_A_TEAPOT)















