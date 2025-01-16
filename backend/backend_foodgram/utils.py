from django.http import HttpResponse
from fpdf import FPDF

from .models import ShoppingCart

import random
import string


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

    Аргументы:
    request -- объект запроса, содержащий информацию о текущем пользователе.

    Возвращает:
    Строку, представляющую список ингредиентов с их количеством и единицами измерения.
    """
    ingredients = []
    # Получаем все рецепты, добавленные в
    # корзину покупок текущим пользователем
    shopping_cart_recipes = ShoppingCart.objects.filter(
        user=request.user
    ).select_related('recipe')
    # Проходим по каждому элементу в корзине покупок
    for item in shopping_cart_recipes:
        # Получаем все ингредиенты для текущего рецепта
        recipe_ingredients = item.recipe.recipeingredients.all()
        # Проходим по всем ингредиентам текущего рецепта
        for recipe_ingredient in recipe_ingredients:
            # Создаем словарь с данными об ингредиенте
            ingredient_data = {
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit':
                    recipe_ingredient.ingredient.measurement_unit,
                'amount': recipe_ingredient.amount
            }
            # Проверяем, существует ли уже этот ингредиент в списке
            existing_ingredient = next(
                (
                    ing for ing in ingredients if
                    ing['name'] == ingredient_data['name']
                    and ing[
                        'measurement_unit'
                    ] == ingredient_data['measurement_unit']
                ),
                None
            )
            # Если ингредиент уже существует, обновляем его количество
            if existing_ingredient:
                existing_ingredient['amount'] = round(
                    existing_ingredient[
                        'amount'
                    ] + ingredient_data['amount'], 3
                )
            else:
                # Если ингредиент новый, добавляем его в список
                ingredients.append(ingredient_data)
    # Формируем строку из списка ингредиентов
    _string = ''
    for ingredient in ingredients:
        _string += (
            f'{ingredient["name"]} — '
            f'{ingredient["amount"]} '
            f'{ingredient["measurement_unit"]}\n'
        )
    return _string  # Возвращаем сформированную строку


def get_shopping_cart_as_txt(request) -> HttpResponse:
    """
    Функция для генерации HttpResponse с текстовым файлом,
    содержащим список покупок.
    """
    ingredients_list = get_ingredients_list(request)
    response = HttpResponse(
        ingredients_list,
        content_type='text/plain'
    )
    response['Content-Disposition'] = (
        'attachment; '
        'filename="shopping_cart.txt"'
    )
    return response


def generate_pdf(request):
    # Получаем список ингредиентов
    ingredients = get_ingredients_list()

    # Создаем объект PDF
    pdf = FPDF()
    pdf.add_page()

    # Устанавливаем шрифт
    pdf.set_font("Arial", size=12)

    # Добавляем содержимое в PDF
    for line in ingredients.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)

    # Создаем HTTP-ответ с PDF-файлом
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ingredients_list.pdf"'

    # Генерируем PDF и выводим его в ответ
    pdf_output = pdf.output().encode('latin-1')  # Получаем PDF как байтовую строку
    response.write(pdf_output)  # Записываем байтовую строку в ответ

    return response
