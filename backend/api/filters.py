from django_filters.rest_framework import CharFilter, FilterSet
from rest_framework.filters import BaseFilterBackend

from recipes.models import Favorite, ShoppingCart


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
    author = CharFilter(field_name='author__id', lookup_expr='exact')
    # tags = CharFilter(field_name='tags__slug', lookup_expr='icontains')
