USER_NAME_LENGTH = 150
RECIPE_NAME_LENGTH = 256
TAG_LENGTH = 32
INGREDIENT_NAME_LENGTH = 128
MEASUREMENT_UNIT_LENGTH = 64
SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
VALIDE_RECIPE_DATA = {
    'ingredients': [
        {'id': 1, 'amount': 50},
        {'id': 2, 'amount': 200}
    ],
    'tags': [1, 2],
    'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',
    'name': 'recipe',
    'text': 'description',
    'cooking_time': 20
}
