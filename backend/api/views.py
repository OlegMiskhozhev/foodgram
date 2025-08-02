from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from backend.paginations import Pagination
from backend.utils import create_shopping_cart, create_short_link
from recipes.models import (Favorite, Ingredient, Link, Recipe, ShoppingCart,
                            Tag)

from .filters import FavoriteShoppingCartFilter, IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, LinkSerializer,
                          RecipeActionSerializer, RecipeSerializer,
                          RecipeUpdateSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    """Представление для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Представление для работы с рецептами."""
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,
                       FavoriteShoppingCartFilter,
                       SearchFilter)
    filterset_class = RecipeFilter
    search_fields = ('tags',)

    def get_permissions(self):
        """Устанавлиевает разрешения в зависимости от действия."""
        if self.action in ('create', 'favorite', 'shopping_cart'):
            self.permission_classes = (IsAuthenticated,)
        elif self.action in ('partial_update', 'destroy'):
            self.permission_classes = (IsAuthorOrReadOnly,)
        return super().get_permissions()

    def get_serializer_class(self):
        """Устанавливает сериализатор обновления рецепта."""
        if self.action == 'partial_update':
            return RecipeUpdateSerializer
        return super().get_serializer_class()

    def partial_update(self, request, *args, **kwargs):
        """Частично обновляет рецепт."""
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    def process_action(self, recipe, model, request):
        """Возвращает ответ при попытке добавить рецепт в список избранного
        или в спискок покупок, в зависмости от того, находится ли рецепт
        в соответствуюшем списке."""
        if request.method == 'POST':
            obj, create = model.objects.get_or_create(
                holder=request.user, recipe=recipe
            )
            if not create:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeActionSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        obj = model.objects.filter(holder=request.user, recipe=recipe)
        if not obj.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('POST', 'DELETE',), detail=True)
    def favorite(self, request, *args, **kwargs):
        """Добавляет или удаляет рецепт в список избранного."""
        return self.process_action(self.get_object(), Favorite, request)

    @action(('POST', 'DELETE',), detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        """Добавляет или удаляет рецепт в список покупок."""
        return self.process_action(self.get_object(), ShoppingCart, request)

    @action(('GET',), detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Возвращает текстовый файл со списком покупок."""
        queryset = request.user.shopping_cart.all()
        recipe_list = [item.recipe for item in queryset]
        shopping_cart = create_shopping_cart(recipe_list)
        response = FileResponse(shopping_cart, content_type='application/text')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt'
        )
        return response

    @action(('GET',), detail=True, url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        """Возвращвает короткую ссылку на рецепт."""
        request_url = request.build_absolute_uri().replace('get-link/', '')
        links = Link.objects.filter(url=request_url)
        if links.exists():
            links = links.get()
        else:
            short_link = create_short_link(request_url)
            links = Link.objects.create(url=request_url, short_link=short_link)
        serializer = LinkSerializer(links)
        return Response(serializer.data, status=status.HTTP_200_OK)


def redirection(request):
    """Представление для обработки короткой ссылки на рецепт."""
    request_url = request.build_absolute_uri().replace('get-link/', '')
    try:
        links = Link.objects.get(short_link=request_url)
        return redirect(links.url.replace('api/', ''))
    except Link.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
