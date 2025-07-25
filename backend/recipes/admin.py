from django.contrib import admin
from django.contrib.auth import get_user_model
from recipes.models import (Favorite, Ingredient, Link, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
    )
    search_fields = ('username', 'email',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount'
    )


class IngredientsInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        IngredientsInline,
    )
    list_display = (
        'name',
        'author',
        'cooking_time',
        'favorite_count'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipes=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'holder',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'holder',
    )


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = (
        'url',
        'short_link'
    )
