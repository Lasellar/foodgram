from django.shortcuts import render
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin
)
from rest_framework.permissions import IsAdminUser

from .models import Tag
from .serializers import TagSerializer


class TagViewSet(CreateModelMixin, ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)


