from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db.models import (
    EmailField, CharField, ImageField
)


class User(AbstractUser):
    """Модель пользователя."""
    email = EmailField(unique=True, max_length=128)
    first_name = CharField(max_length=32)
    last_name = CharField(max_length=32)
    username = CharField(max_length=32, unique=True)
    avatar = ImageField(
        'Аватар', upload_to='avatars/', blank=True, null=True
    )
    password = CharField(max_length=32)

