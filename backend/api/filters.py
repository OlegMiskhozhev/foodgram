from django_filters.rest_framework import (CharFilter, FilterSet,
                                           ModelMultipleChoiceFilter)
from recipes.models import Favorite, ShoppingCart, Tag
from rest_framework.filters import BaseFilterBackend


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
            favorite_obj = Favorite.objects.get(holder=holder)
            return favorite_obj.recipes.all()
        if shopping_cart:
            shopping_cart_obj = ShoppingCart.objects.get(holder=holder)
            return shopping_cart_obj.recipes.all()
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
