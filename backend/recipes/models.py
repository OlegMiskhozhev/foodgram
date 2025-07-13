from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from backend import constants

User = get_user_model()


class Tag(models.Model):

    name = models.CharField(
        'Название',
        max_length=constants.TAG_LENGTH,
        unique=True
    )
    slug = models.CharField(
        'Слаг',
        max_length=constants.TAG_LENGTH,
        unique=True,
        validators=[RegexValidator(r'^[-a-zA-Z0-9_]+$',)]
    )


class Ingredient(models.Model):

    name = models.CharField(
        'Название',
        max_length=constants.INGREDIENT_NAME_LENGTH,
    )
    name = models.CharField(
        'Единицы измерения',
        max_length=constants.MEASUREMENT_UNIT_LENGTH,
    )


class Recipe(models.Model):

    name = models.CharField(
        'Название',
        max_length=constants.RECIPE_NAME_LENGTH
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        default=None
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField('Количество')


class Favorite(models.Model):
    holder = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipes = models.ManyToManyField(Recipe, verbose_name='Избранные рецепты')
