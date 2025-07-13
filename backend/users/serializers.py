import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers


User = get_user_model()


class CustomUserMixin:
    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = CustomUserMixin.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return False if (
            user.is_anonymous or obj not in user.subscription.all()) else True


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = CustomUserMixin.Meta.fields + ('password',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerialaizer(UserSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta(UserSerializer.Meta):
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar')
        instance.save()
        return instance


class SubscriptionsSerialaizer(UserSerializer):
    subscription = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('subscription',)


class SubscribeSerialaizer(UserSerializer):
    pass
