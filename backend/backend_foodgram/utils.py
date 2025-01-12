import random
import string

from django.shortcuts import get_object_or_404

from .models import Recipe, ShoppingCart, RecipeIngredient


def generate_short_link(request):
    random.seed(request.path)
    short_link = ''.join(
        [
            random.choice(string.ascii_letters + string.digits)
            for _ in range(3)
        ]
    )
    return short_link


def generate_full_short_url(link):
    return {
        'short-link': f'https://foodgram_lasellar.ddns.com/s/{link}'
    }


def get_ingredients_list(request):
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
                existing_ingredient['amount'] += ingredient_data['amount']
            else:
                ingredients.append(ingredient_data)
    _string = ''
    for ingredient in ingredients:
        _string += (
            f'{ingredient["name"]} - '
            f'{ingredient["amount"]} '
            f'{ingredient["measurement_unit"]}\n'
        )
    return _string
