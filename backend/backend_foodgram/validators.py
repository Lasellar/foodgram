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
        fields_with_errors = []
        for field, error_message in errors.items():
            value = data.get(field)
            if (
                field == 'email'
                and User.objects.filter(email=value).exists()
            ):
                fields_with_errors.append(field)
            if (
                field == 'username'
                and User.objects.filter(username=value).exists()
            ):
                fields_with_errors.append(field)
            if (
                value.lower() in settings.FORBIDDEN_CASES[field]
            ):
                fields_with_errors.append(field)
        if fields_with_errors:
            raise ValidationError(
                {'field_name': fields_with_errors}
            )
        return data


