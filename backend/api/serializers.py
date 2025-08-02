from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)

from backend.utils import Base64ImageField
from recipes.models import Ingredient, Link, Recipe, RecipeIngredient, Tag
from users.serializers import UserSerializer


class TagSerializer(ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""
    id = PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    name = SlugRelatedField(
        source='ingredient', slug_field='name', read_only=True
    )
    measurement_unit = SlugRelatedField(
        source='ingredient', slug_field='measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def validate_amount(self, value):
        """Проверяет соответствие данных поля amount требованиями проекта."""
        if value < 1:
            raise ValidationError(
                'Количество должно быть больше либо равно 1.'
            )
        return value


class RecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe."""
    image = Base64ImageField(required=True, allow_null=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredients', many=True
    )
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Формирует данные для поля is_favorited."""
        user = self.context.get('request').user
        return True if not user.is_anonymous and obj.favorites.filter(
            holder=user, recipe=obj).exists() else False

    def get_is_in_shopping_cart(self, obj):
        """Формирует данные для поля is_in_shopping_cart."""
        user = self.context.get('request').user
        return True if not user.is_anonymous and obj.shopping_cart.filter(
            holder=user, recipe=obj).exists() else False

    def to_representation(self, instance):
        """Изменяет вывод данных для поля ingredients рецепта."""
        data = super().to_representation(instance)
        tags = data.get('tags')
        data['tags'] = []
        for tag_id in tags:
            tag_obj = Tag.objects.get(id=tag_id)
            data['tags'].append(TagSerializer(tag_obj).data)
        return data

    def check_empty_repeat(self, items, field):
        """Проверяет, что список элементов поля не пустой,
        и не содержит повторяющиеся элементы."""
        if not len(items):
            raise ValidationError({field: 'Поле не должно быть пустым.'})
        item_list = set()
        for item in items:
            item_list.add(item)
        if len(items) != len(item_list):
            raise ValidationError({field: 'Повторы не допустимы.'})

    def validate(self, attrs):
        """Проверяет соответствие данных полуй tags и ingredients
        требованиями проекта."""
        tags = attrs.get('tags')
        self.check_empty_repeat(tags, 'tags')
        ingredients = attrs.get('recipeingredients')
        ingredients_list = [
            ingredient.get('ingredient') for ingredient in ingredients
        ]
        self.check_empty_repeat(ingredients_list, 'ingredients')
        return super().validate(attrs)

    def add_ingredients(self, recipe, ingredients):
        """Добавляет ингредиенты с указанием количества в рецепт."""
        ingredients_to_add = []
        for ingredient in ingredients:
            ingredients_to_add.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'))
            )
        RecipeIngredient.objects.bulk_create(ingredients_to_add)

    def add_tags(self, recipe, tags):
        """Добавляет теги в рецепт."""
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        """Создает объект модели Recipe."""
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data)
        self.add_ingredients(recipe, ingredients)
        self.add_tags(recipe, tags)
        return recipe


class RecipeUpdateSerializer(RecipeSerializer):
    """Сериализатор для обновления объекта модели Recipe."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta(RecipeSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        """Обновляет объект модели Recipe."""
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        self.add_ingredients(instance, ingredients)
        self.add_tags(instance, tags)
        return instance


class RecipeActionSerializer(ModelSerializer):
    """Сериализатор для вывода данных при выполнении действий
    по добалению рецепта в список избранного или в список покупок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class LinkSerializer(ModelSerializer):
    """Сериализатор для вывода данных при запросе короткой ссылки."""
    class Meta:
        model = Link
        fields = ('short_link',)

    def to_representation(self, instance):
        """Формирует данные для вывода поля short-link."""
        data = super().to_representation(instance)
        representation = {'short-link': data['short_link']}
        return representation
