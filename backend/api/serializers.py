from rest_framework.serializers import (IntegerField,
                                        ModelSerializer,
                                        SerializerMethodField,
                                        ValidationError)

from backend.utils import Base64ImageField
from recipes.models import (Favorite,
                            Ingredient,
                            Link,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)

from users.serializers import UserSerializer


class TagSerializer(ModelSerializer):
    id = IntegerField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('name', 'slug')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'amount',)
        depth = 1

    def to_representation(self, instance):
        data = super().to_representation(instance)
        representation = {
            'id': data['ingredient']['id'],
            'name': data['ingredient']['name'],
            'measurement_unit': data['ingredient']['measurement_unit'],
            'amount': data['amount']
        }
        return representation

    def validate_amount(self, value):
        if value < 1:
            raise ValidationError(
                'Количество должно быть больше либо равно 1.')
        return value


class RecipeSerializer(ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredients', many=True)
    tags = TagSerializer(many=True)

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
        depth = 1

    def check_favorite_shopping_cart(self, model, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            field, _ = model.objects.get_or_create(holder=user)
        else:
            return False
        return True if obj in field.recipes.all() else False

    def get_is_favorited(self, obj):
        return self.check_favorite_shopping_cart(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.check_favorite_shopping_cart(ShoppingCart, obj)

    def to_internal_value(self, data):
        tags = data.get('tags')
        if tags:
            tags_obj = []
            for tag in tags:
                tags_obj.append({'id': tag})
            data['tags'] = tags_obj
        return super().to_internal_value(data)

    def validate(self, attrs):
        if not attrs.get('recipeingredients'):
            raise ValidationError({'ingredients': 'Обязательное поле.'})
        if not attrs.get('tags'):
            raise ValidationError({'tags': 'Обязательное поле.'})
        if not attrs.get('name'):
            raise ValidationError({'name': 'Обязательное поле.'})
        if not attrs.get('text'):
            raise ValidationError({'text': 'Обязательное поле.'})
        if not attrs.get('cooking_time'):
            raise ValidationError({'cooking_time': 'Обязательное поле.'})
        return super().validate(attrs)

    def check_tags_ingredients(self, model, value):
        if not len(value):
            raise ValidationError('Поле не должно быть пустым.')
        objects = set()
        for item in value:
            id = item.get('id')
            try:
                model.objects.get(id=id)
            except model.DoesNotExist:
                raise ValidationError('Не существующий объект.')
            objects.add(id)
        if len(value) != len(objects):
            raise ValidationError('Повторы не допустимы.')

    def validate_tags(self, value):
        self.check_tags_ingredients(Tag, value)
        return value

    def validate_ingredients(self, value):
        self.check_tags_ingredients(Ingredient, value)
        return value
    
    def add_ingredients(self, recipe, ingredients):
        for item in ingredients:
            ingredient = Ingredient.objects.get(id=item.get('id'))
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=item.get('amount')
            )

    def add_tags(self, recipe, tags):
        for item in tags:
            tag = Tag.objects.get(id=item.get('id'))
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(recipe, ingredients)
        self.add_tags(recipe, tags)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.ingredients.clear()
        ingredients = validated_data.get('recipeingredients')
        self.add_ingredients(instance, ingredients)
        instance.tags.clear()
        tags = validated_data.get('tags')
        self.add_tags(instance, tags)
        return instance


class ActionSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class LinkSerializer(ModelSerializer):

    class Meta:
        model = Link
        fields = ('short_link',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        representation = {'short-link': data['short_link']}
        return representation
