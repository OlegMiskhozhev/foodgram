from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from backend import constants

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""
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

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tag'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField(
        'Название',
        max_length=constants.INGREDIENT_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=constants.MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredient'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_with_unit'
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""
    name = models.CharField(
        'Название',
        max_length=constants.RECIPE_NAME_LENGTH
    )
    text = models.TextField(
        'Описание',
    )
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
        verbose_name='Ингредиент',
        through='RecipeIngredient'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель для связи ингредиентов с рецептами."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        verbose_name = 'ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        default_related_name = 'recipeingredients'

    def __str__(self):
        return self.recipe.name


class ActionModel(models.Model):
    """Базовая модель для списков подписок и покупок."""
    holder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class Favorite(ActionModel):
    """Модель для списков подписок."""
    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['holder', 'recipe'],
                name='unique_user_favorite'
            ),
        ]

    def __str__(self):
        return self.holder.username


class ShoppingCart(ActionModel):
    """Модель для списков покупок."""
    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=['holder', 'recipe'],
                name='unique_user_shopping_cart'
            ),
        ]

    def __str__(self):
        return self.holder.username


class Link(models.Model):
    """Модель для коротких ссылок на рецепты."""
    url = models.URLField()
    short_link = models.URLField()

    class Meta:
        verbose_name = 'ссылки'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return self.short_link
