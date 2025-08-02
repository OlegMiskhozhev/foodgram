from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import (Favorite, Ingredient, Link, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ['avatar']}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ['email', 'first_name', 'last_name']}),)
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'recipes_count',
        'subscriptions_count',
        'avatar',
    )
    search_fields = ('username', 'email',)

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Количество подписчиков')
    def subscriptions_count(self, obj):
        return obj.subscribed.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subscribed_on'
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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

    @admin.display(description='Добавленно в избранное')
    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'holder',
        'recipe'
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'holder',
        'recipe'
    )


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = (
        'url',
        'short_link'
    )
