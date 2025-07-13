from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser.conf import settings
from djoser.views import UserViewSet


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = settings.PERMISSIONS.me
        if self.action == 'avatar':
            self.permission_classes = settings.PERMISSIONS.avatar
        if self.action == 'subscriptions':
            self.permission_classes = settings.PERMISSIONS.subscriptions
        if self.action == 'subscribe':
            self.permission_classes = settings.PERMISSIONS.subscribe
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'avatar':
            return settings.SERIALIZERS.avatar
        if self.action == 'subscriptions':
            return settings.SERIALIZERS.subscriptions
        if self.action == 'subscribe':
            return settings.SERIALIZERS.subscribe
        return super().get_serializer_class()

    @action(('PUT', 'DELETE',), detail=True, lookup_field='me')
    def avatar(self, request, *args, **kwargs):
        instance = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                data=request.data, instance=instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            instance.avatar = None
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('GET',), detail=False)
    def subscriptions(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(('POST', 'DELETE',), detail=True)
    def subscribe(self, request, *args, **kwargs):
        subscribe_user = self.get_object()
        if request.method == 'POST':
            request.user.subscription.add(subscribe_user)
            return Response(status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            request.user.subscription.remove(subscribe_user)
            return Response(status=status.HTTP_204_NO_CONTENT)
