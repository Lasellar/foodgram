from backend.settings import DATAFILES_DIR

import json


def load_json():
    ingredients_list = open_json()
    print('creating ingredients objects...')
    for ingredient in ingredients_list:
        Ingredient.objects.get_or_create(
            name=ingredient['name'],
            measurement_unit=ingredient['measurement_unit']
        )
    print('created')


def open_json():
    path = DATAFILES_DIR / 'ingredients.json'
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as ex:
        print(ex)
        return


if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    from backend_foodgram.models import Ingredient
    load_json()
