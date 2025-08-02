from django_filters.rest_framework import (CharFilter, FilterSet,
                                           ModelMultipleChoiceFilter)
from rest_framework.filters import BaseFilterBackend

from recipes.models import Tag


class FavoriteShoppingCartFilter(BaseFilterBackend):
    """Фильтр для вывода списка рецептов, находящихся
    в списке избранного или списке покупок текущего пользователя."""

    def filter_queryset(self, request, queryset, view):
        holder = request.user
        favorite = request.query_params.get('is_favorited')
        shopping_cart = request.query_params.get('is_in_shopping_cart')
        if holder.is_anonymous:
            return queryset
        if favorite:
            favorite_objects = holder.favorites.all()
            favorite_recipes = [obj.recipe for obj in favorite_objects]
            return favorite_recipes
        if shopping_cart:
            shopping_cart_objects = holder.shopping_cart.all()
            shopping_cart_recipes = [
                obj.recipe for obj in shopping_cart_objects
            ]
            return shopping_cart_recipes
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр для вывода списка игредиентов по имени."""
    name = CharFilter(lookup_expr='icontains')


class RecipeFilter(FilterSet):
    """Фильтр для вывода списка рецептов по автору и тегам."""
    author = CharFilter(field_name='author__id')
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
