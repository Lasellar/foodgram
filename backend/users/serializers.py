from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from rest_framework.serializers import (
    Serializer, RegexField, EmailField, CharField
)
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.validators import UniqueValidator

User = get_user_model()


class SignUpSerializer(Serializer):
    first_name = CharField(max_length=20, required=True)
    last_name = CharField(max_length=20, required=True)
    username = RegexField(
        regex=r'^[\w.@+-]+\Z', max_length=32, required=True
    )
    email = EmailField(max_length=256, required=True)
    password = CharField(max_length=1024, required=True)

    def validate_username(self, value):
        """Запрет на использование запрещенных username."""
        if value.lower() in settings.FORBIDDEN_CASES['username']:
            raise ValidationError('Недопустимый username.')
        return value

    def validate(self, attrs):
        """Проверка всех полей на запретность и """
        forbidden_cases = {
            'first_name': 'Недопустимое имя.',
            'last_name': 'Недопустимая фамилия.',
            'username': 'Недопустимый username.',
            'email': 'Недопустимый email.',
            'password': 'Недопустимый password.'
        }

        for field, error_message in forbidden_cases.items():
            value = attrs.get(field)
            if (field == 'email') and (
                User.objects.filter(email=value).exists()
            ):
                raise ValidationError(
                    {'email': 'Пользователь с таким email уже существует.'}
                )
            if (field == 'username') and (
                User.objects.filter(username=value).exists()
            ):
                raise ValidationError(
                    {
                        'username': 'Пользователь с таким username '
                                    'уже существует.'
                    }
                )
            if value and value.lower() in settings.FORBIDDEN_CASES[field]:
                raise ValidationError({field: error_message})
        return attrs

    def create(self, validated_data):
        """Создание нового пользователя и отправка кода подтверждения."""
        user = User.objects.create(**validated_data)
        self.create_or_update_confirmation_code(user)
        return user

    def create_or_update_confirmation_code(self, user):
        confirmation_code = get_random_string(length=6)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Код подтверждения для FoodGram',
            message=f'Добро пожаловать на FoodGram! '
                    f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(user.email,),
            fail_silently=False
        )



