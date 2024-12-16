from django.db.models import (
    Model, CharField, SlugField
)


class Tag(Model):
    name = CharField(verbose_name='Название', max_length=16)
    slug = SlugField(verbose_name='Слаг', max_length=32)

