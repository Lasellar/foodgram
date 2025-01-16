from django.http import HttpResponse

from .models import ShoppingCart

import random
import string
import pdfkit


def generate_short_link():
    """
    Функция для генерации случайного slug
    для короткой ссылки на рецепт.
    """
    short_link = ''.join(
        [
            random.choice(string.ascii_letters + string.digits)
            for _ in range(3)
        ]
    )
    return short_link


def generate_full_short_url(link):
    """
    Функция для генерации json-ответа со сгенерированной
    короткой ссылкой на рецепт.
    """
    return {
        'short-link': f'https://lasellarfoodgram.ddns.net/s/{link}'
    }


def get_ingredients_list(request):
    """
    Функция для генерации строки со списком
    ингредиентов из списка покупок.
    """
    ingredients = []
    shopping_cart_recipes = ShoppingCart.objects.filter(
        user=request.user
    ).select_related('recipe')
    for item in shopping_cart_recipes:
        recipe_ingredients = item.recipe.recipeingredients.all()
        for recipe_ingredient in recipe_ingredients:
            ingredient_data = {
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit':
                    recipe_ingredient.ingredient.measurement_unit,
                'amount': recipe_ingredient.amount
            }
            existing_ingredient = next(
                (
                    ing for ing in ingredients if
                    ing['name'] == ingredient_data['name']
                    and ing['measurement_unit']
                    == ingredient_data['measurement_unit']
                ),
                None
            )
            if existing_ingredient:
                existing_ingredient['amount'] = round(
                    existing_ingredient[
                        'amount'
                    ] + ingredient_data['amount'], 3
                )
            else:
                ingredients.append(ingredient_data)
    _string = ''
    for ingredient in ingredients:
        _string += (
            f'{ingredient["name"]} — '
            f'{ingredient["amount"]} '
            f'{ingredient["measurement_unit"]}\n'
        )
    return _string


def get_shopping_cart_as_txt(request):
    """
    Функция для генерации ответа с текстовым файлом,
    содержащим список покупок.
    """
    ingredients_list = get_ingredients_list(request)
    response = HttpResponse(
        ingredients_list,
        content_type='text/plain'
    )
    response['Content-Disposition'] = (
        'attachment; '
        'filename="shopping_cart.txt'
    )
    return response


def get_shopping_cart_as_pdf(request):
    """
    Функция для генерации ответа с pdf-файлом,
    содержащим список покупок.
    """
    ingredients_list = get_ingredients_list(request)
    pdf = pdfkit.from_string(ingredients_list)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; '
        'filename="shopping_cart.pdf'
    )
    return response
