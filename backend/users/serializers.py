from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (PrimaryKeyRelatedField, Serializer,
                                        SerializerMethodField)

from backend.utils import Base64ImageField

User = get_user_model()


class UserMixin:
    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class UserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserMixin.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            True if not user.is_anonymous
            and obj in user.subscription.all()
            else False
        )


class UserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = UserMixin.Meta.fields + ('password',)


class AvatarSerialaizer(UserSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta(UserSerializer.Meta):
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar')
        instance.save()
        return instance


class RecipeSubscrubeSerializer(Serializer):
    name = PrimaryKeyRelatedField(read_only=True)
    id = PrimaryKeyRelatedField(read_only=True)
    cooking_time = PrimaryKeyRelatedField(read_only=True)
    image = Base64ImageField(required=True, allow_null=True)


class SubscribedUserSerialaizer(UserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        if limit:
            limit = int(limit)
        queryset = obj.recipes.all()
        serializer = RecipeSubscrubeSerializer(queryset[:limit], many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
