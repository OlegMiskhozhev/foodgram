from django.http import FileResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from backend.paginations import Pagination
from backend.utils import create_short_link, create_shopping_cart
from recipes.models import (Favorite,
                            Ingredient,
                            Link,
                            Recipe,
                            ShoppingCart,
                            Tag)

from .filters import FavoriteShoppingCartFilter, IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (ActionSerializer,
                          IngredientSerializer,
                          LinkSerializer,
                          RecipeSerializer,
                          TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
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
        if self.action in ('create', 'favorite', 'shopping_cart'):
            self.permission_classes = (IsAuthenticated,)
        elif self.action in ('partial_update', 'destroy'):
            self.permission_classes = (IsAuthorOrReadOnly,)
        return super().get_permissions()

    def perform_create(self, serializer):
        recipe = serializer.save(author=self.request.user)
        return recipe

    def process_action(self, recipe, model, request):
        obj, _ = model.objects.get_or_create(holder=request.user)
        if request.method == 'POST':
            if recipe in obj.recipes.all():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            obj.recipes.add(recipe)
            serializer = ActionSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if recipe not in obj.recipes.all():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            obj.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('POST', 'DELETE',), detail=True)
    def favorite(self, request, *args, **kwargs):
        return self.process_action(self.get_object(), Favorite, request)

    @action(('POST', 'DELETE',), detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        return self.process_action(self.get_object(), ShoppingCart, request)

    @action(('GET',), detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        recipe_list = request.user.shopping_cart.recipes.all()
        shopping_cart = create_shopping_cart(recipe_list)
        file_name = 'shopping_cart.txt'
        response = FileResponse(shopping_cart)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    @action(('GET',), detail=True, url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        url = request.build_absolute_uri().replace('get-link/', '')
        short_link = create_short_link(url)
        links = Link.objects.create(url=url, short_link=short_link)
        serializer = LinkSerializer(links)
        return Response(serializer.data, status=status.HTTP_200_OK)


def redirection(request):
    try:
        links = Link.objects.get(short_link=request.build_absolute_uri())
        return redirect(links.url)
    except Link.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
