from django.contrib.auth import get_user_model, authenticate
from django.core.files.base import ContentFile
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .serializers import (
    UserSignUpSerializer, UserSerializer
)
from .validators import SignUpValidator

import base64

User = get_user_model()


class SignUpView(APIView, SignUpValidator):
    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'email': user.email,
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'password': serializer.validated_data['password']
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
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
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'detail': 'Method Not Allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_staff:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'detail': 'Method Not Allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


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
