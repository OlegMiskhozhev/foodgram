from django.contrib.auth import get_user_model
from django.db.models import Count
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.paginations import Pagination

from .models import Subscription

User = get_user_model()


class UserViewSet(UserViewSet):
    """Представление для обработки запросов к модели пользователей."""
    pagination_class = Pagination

    def get_permissions(self):
        """Устанавливает разрешения в зависимости от выполняемого действия."""
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
        """Устанавливает сериализатор в зависимости
        от выполняемого действия."""
        if self.action == 'avatar':
            return settings.SERIALIZERS.avatar
        elif self.action == 'subscriptions':
            return settings.SERIALIZERS.subscriptions
        elif self.action == 'subscribe':
            return settings.SERIALIZERS.subscribe
        return super().get_serializer_class()

    @action(('PUT', 'DELETE',), detail=True, lookup_field='me')
    def avatar(self, request, *args, **kwargs):
        """Присваивает и удаляет аватар пользователя."""
        instance = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                data=request.data, instance=instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        instance.avatar = None
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_subscription_instance(self, request):
        """Возвращает список объектов подписок текущего пользователя."""
        return request.user.subscriber.annotate(
            recipes_count=Count('subscribed_on__recipes')
        ).select_related('subscribed_on')

    @action(('GET',), detail=False)
    def subscriptions(self, request, *args, **kwargs):
        """Возвращает список подписок текущего пользователя."""
        instance = self.get_subscription_instance(request)
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(('POST', 'DELETE',), detail=True)
    def subscribe(self, request, *args, **kwargs):
        """Обрабатывает запросы на подписку и удаление подписки
        текущего пользователя."""
        if request.user == self.get_object():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            subscription, create = Subscription.objects.get_or_create(
                user=request.user,
                subscribed_on=self.get_object()
            )
            if not create:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            instance = self.get_subscription_instance(request).get(
                subscribed_on=self.get_object()
            )
            serializer = self.get_serializer(instance=instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = request.user.subscriber.filter(
            subscribed_on=self.get_object()
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
