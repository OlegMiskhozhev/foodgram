import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


def create_shopping_cart(recipe_list):
    ingredients_list = {}
    for recipe in recipe_list:
        ingredients = recipe.recipeingredients.all()
        for ingredient in ingredients:
            name = ingredient.ingredient.name
            unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount
            if ingredients_list.get((name, unit)):
                ingredients_list[(name, unit)] += amount
            else:
                ingredients_list[(name, unit)] = amount
    shopping_cart = 'Список покупок:\n\n'
    for ingredient, amount in ingredients_list.items():
        shopping_cart += (
            f'\t\N{BULLET} {ingredient[0]} ({ingredient[-1]}) - {amount}\n')
    return shopping_cart


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)
