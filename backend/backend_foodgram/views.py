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

from .filters import IngredientFilter
from .models import Tag, Ingredient, Recipe, ShoppingCart, Favorite
from users.models import Subscription
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeGETSerializer, ShoppingCartSerializer, FavoriteSerializer,
    UserSubscribeSerializer, UserSubscribeRepresentSerializer,
    UserGETSerializer, UserSignUpSerializer
)
from .validators import SignUpValidator

import base64

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
    pagination_class = None

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
            return Response({'token': token.key}, status=status.HTTP_200_OK)
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
    queryset = User.objects.all()
    serializer_class = UserGETSerializer
    http_method_names = ('get', 'post')

    def get_permissions(self):
        """
        Метод, определяющий разрешения на доступ для конкретных методов.
        """
        if (
            self.request.method == 'POST'
            and self.kwargs.get('pk') == 'set_password'
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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Метод, отвечающий за регистрацию пользователя.
        """
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('post',), url_path='set_password')
    def set_password(self, request):
        """
        Метод, отвечающий за смену пароля.
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

    def retrieve(self, request, *args, **kwargs):
        """
        Метод, отвечающий за получение профиля текущего пользователя и
        получение пользователя по его id.
        """
        instance = self.get_object()
        if not instance:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AvatarView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user
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
            {'error': 'No avatar provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        user = request.user
        user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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















