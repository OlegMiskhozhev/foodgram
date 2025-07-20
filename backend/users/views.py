from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.paginations import Pagination

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = Pagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = settings.PERMISSIONS.me
        elif self.action == 'avatar':
            self.permission_classes = settings.PERMISSIONS.avatar
        elif self.action == 'subscriptions':
            self.permission_classes = settings.PERMISSIONS.subscriptions
        elif self.action == 'subscribe':
            self.permission_classes = settings.PERMISSIONS.subscribe
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'avatar':
            return settings.SERIALIZERS.avatar
        elif self.action == 'subscriptions':
            return settings.SERIALIZERS.subscriptions
        elif self.action == 'subscribe':
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
        instance = request.user.subscription.all()
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(('POST', 'DELETE',), detail=True)
    def subscribe(self, request, *args, **kwargs):
        subscribe_user = self.get_object()
        subscriptions = request.user.subscription
        if subscribe_user == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            if subscribe_user in subscriptions.all():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscriptions.add(subscribe_user)
            serializer = self.get_serializer(instance=subscribe_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if subscribe_user not in subscriptions.all():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscriptions.remove(subscribe_user)
            return Response(status=status.HTTP_204_NO_CONTENT)
