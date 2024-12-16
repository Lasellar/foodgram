from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.exceptions import ValidationError


User = get_user_model()


class SignUpValidator:
    def validate(self, data):
        """
        Проверка всех полей на запретность и
        существование пользователя в БД.
        """
        errors = {
            'first_name': 'Недопустимое имя.',
            'last_name': 'Недопустимая фамилия.',
            'username': 'Недопустимый username.',
            'email': 'Недопустимый email.',
            'password': 'Недопустимый пароль.'
        }

        for field, error_message in errors.items():
            value = data.get(field)
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
        return data
