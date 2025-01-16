from backend.settings import DATAFILES_DIR

import csv


def load_csv():
    data = open_csv()
    print('creating ingredients objects...')
    for ingredient in data:
        Ingredient.objects.get_or_create(
            name=ingredient[0],
            measurement_unit=ingredient[1]
        )
    print('created')


def open_csv():
    path = DATAFILES_DIR / 'ingredients.csv'
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return list(csv.reader(file))
    except Exception as ex:
        print(ex)
        return


if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    from backend_foodgram.models import Ingredient
    load_csv()
