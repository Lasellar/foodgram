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
    ingredients = [{'123': 123}]
    shopping_cart_recipes = ShoppingCart.objects.filter(
        user=request.user
    ).select_related('recipe')
    for recipe_item in shopping_cart_recipes:
        recipe_ingredients = recipe_item.recipe.recipeingredients.all()
        for recipe_ingredient in recipe_ingredients:
            ingredient_name = recipe_ingredient.ingredient.name
            ingredient_amount = RecipeIngredient.objects.get(
                recipe=recipe_item.id, ingredient=recipe_ingredient.ingredient.id
            ).amount
            ingredient_measurement_unit = recipe_ingredient.ingredient.measurement_unit
            for ingredient in ingredients:
                ingredient_keys = ingredient.keys()
                if (
                    str(ingredient_name) in ingredient_keys
                    and str(ingredient_measurement_unit) in ingredient_keys
                ):
                    ingredient['amount'] += ingredient_amount
                else:
                    ingredients.append(
                        {
                            'name': ingredient_name,
                            'measurement_unit': ingredient_measurement_unit,
                            'amount': ingredient_amount
                        }
                    )
    return ingredients
