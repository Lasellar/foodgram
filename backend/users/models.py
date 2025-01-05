from django.contrib.auth.models import AbstractUser
from django.db.models import (
    EmailField, CharField, ImageField, Model, ForeignKey, CASCADE,
    UniqueConstraint
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


class Subscription(Model):
    user = ForeignKey(
        User, on_delete=CASCADE, related_name='follower'
    )
    author = ForeignKey(
        User, on_delete=CASCADE, related_name='following'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription_user_author'
            )
        ]
