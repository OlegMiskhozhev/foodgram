from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField, Serializer,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from backend.utils import Base64ImageField

from .models import Subscription

User = get_user_model()


class UserMixin:
    """Миксин сериализаторов модели пользователей."""
    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name'
        )


class UserSerializer(UserSerializer):
    """Сериализатор для модели пользователей."""
    is_subscribed = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserMixin.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Проверяет наличие пользователя в списке подписок
        текущего пользователя."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            subscription = user.subscriber.filter(subscribed_on=obj)
        return (
            True if not user.is_anonymous
            and subscription.exists()
            else False
        )


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""
    class Meta:
        model = User
        fields = UserMixin.Meta.fields + ('password',)


class AvatarSerialaizer(UserSerializer):
    """Сериализатор для добавления и удаления аватара пользователя."""
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta(UserSerializer.Meta):
        fields = ('avatar',)

    def update(self, instance, validated_data):
        """Обновляет аватар пользователя."""
        instance.avatar = validated_data.get('avatar')
        instance.save()
        return instance


class RecipeSubscrubeSerializer(Serializer):
    """Сериализатор для списка рецептов подписываемого пользователя."""
    name = PrimaryKeyRelatedField(read_only=True)
    id = PrimaryKeyRelatedField(read_only=True)
    cooking_time = PrimaryKeyRelatedField(read_only=True)
    image = Base64ImageField(required=True, allow_null=True)


class SubscribedUserSerialaizer(UserSerializer):
    """Сериализатор для подписки на пользователя."""
    subscribed_on = UserSerializer(read_only=True)
    recipes = SerializerMethodField()
    recipes_count = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('subscribed_on', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Возвращает список рецептов пользователя."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                raise ValidationError('Некорректный запрос')
        queryset = obj.subscribed_on.recipes.all()
        serializer = RecipeSubscrubeSerializer(queryset[:limit], many=True)
        return serializer.data

    def to_representation(self, instance):
        """Изменяет вывод данных для запроса на подписку."""
        data = super().to_representation(instance)
        user = data.pop('subscribed_on')
        recipes = data.pop('recipes')
        recipes_count = data.pop('recipes_count')
        data = user
        data['recipes'] = recipes
        data['recipes_count'] = recipes_count
        return data


class SubscribeCreateSerialaizer(ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'subscribed_on'],
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate(self, data):
        if data['user'] == data['subscribed_on']:
            raise ValidationError(
                'Нельзя подписаться на самого себя.')
        return data
