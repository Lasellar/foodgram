from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from rest_framework.serializers import (
    Serializer,
)
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.validators import UniqueValidator
