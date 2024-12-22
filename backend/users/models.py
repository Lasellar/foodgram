from django.contrib.auth.models import AbstractUser
from django.db.models import (
    EmailField, CharField, ImageField
)


class User(AbstractUser):
    """Модель пользователя."""
    email = EmailField(unique=True, max_length=254)
    first_name = CharField(max_length=150)
    last_name = CharField(max_length=150)
    username = CharField(max_length=150, unique=True)
    avatar = ImageField(
        'Аватар', upload_to='avatars/', blank=True, null=True
    )
    password = CharField()

