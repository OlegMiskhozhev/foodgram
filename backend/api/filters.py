from django_filters.rest_framework import (CharFilter, FilterSet,
                                           ModelMultipleChoiceFilter)
from recipes.models import Favorite, ShoppingCart, Tag
from rest_framework.filters import BaseFilterBackend


class FavoriteShoppingCartFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        holder = request.user
        favorite = request.query_params.get('is_favorited')
        print('favorite: ', favorite)
        shooping_cart = request.query_params.get('is_in_shopping_cart')
        if holder.is_anonymous:
            return queryset
        if favorite:
            favorite_obj = Favorite.objects.get(holder=holder)
            return favorite_obj.recipes.all()
        if shooping_cart:
            shooping_cart_obj = ShoppingCart.objects.get(holder=holder)
            return shooping_cart_obj.recipes.all()
        return queryset


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')


class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author__id')
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
