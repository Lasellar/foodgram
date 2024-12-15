from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import (
    EmailField,
)


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Аутентифицированный пользователь'),
        (ADMIN, 'Администратор')
    ]

    email = EmailField(unique=True, blank=False, null=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        """Запрет на использование 'me' в качестве имени пользователя."""
        if (
            self.username.lower() == 'me'
        ) or (
            self.username.lower() == 'user'
        ) or (
            self.username.lower() == 'username'
        ):
            raise ValidationError('Недопустимый username')
        super().clean()

    def save(self, *args, **kwargs):
        self.role = self.ADMIN if self.is_superuser else self.USER
        self.is_staff = self.role == self.ADMIN
        super().save(*args, **kwargs)

