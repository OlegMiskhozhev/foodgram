from django.contrib.auth import get_user_model
from django_filters.rest_framework import (BooleanFilter,
                                           CharFilter,
                                           FilterSet)
from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author__id', lookup_expr='exact')
    tags = CharFilter(field_name='tags__slug', lookup_expr='icontains')
    is_favorited = BooleanFilter()
    is_in_shopping_cart = BooleanFilter()
