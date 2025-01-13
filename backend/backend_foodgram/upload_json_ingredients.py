from django.core.management import BaseCommand


from backend.backend.settings import DATAFILES_DIR

import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')
django.setup()

from .models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_json()


def load_json():
    ingredients_list = open_json()
    for ingredient in ingredients_list:
        ingredient, created = Ingredient.objects.get_or_create(
            name=ingredient['name'],
            measurement_unit=ingredient['measurement_unit']
        )
        if created:
            print('created', Ingredient.objects.count)


def open_json():
    path = DATAFILES_DIR / 'ingredients.json'
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as ex:
        print(ex)
        return


open_json()

