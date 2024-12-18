from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    ModelSerializer, CharField
)

User = get_user_model()


class SignUpSerializer(ModelSerializer):
    password = CharField(write_only=True)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'avatar', 'password'
        )


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name'
        )
