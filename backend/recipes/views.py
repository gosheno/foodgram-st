from api.paginations import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from django.core.cache import cache
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeMinifiedSerializer, RecipeSerializer)
from .utils import generate_shopping_list


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    queryset = Recipe.objects.prefetch_related(
        'recipe_ingredients__ingredient',
        'favorited_by',
        'in_shopping_carts'
    ).select_related('author')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if not user.is_authenticated:
            context.update({
                'favorited_ids': set(),
                'shopping_cart_ids': set()
            })
            return context

        favorites = set(Favorite.objects.filter(
            user=user).values_list('recipe_id', flat=True))
        carts = set(ShoppingCart.objects.filter(
            user=user).values_list('recipe_id', flat=True))

        context.update({
            'favorited_ids': favorites,
            'shopping_cart_ids': carts
        })
        return context

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        favorite_exists = Favorite.objects.filter(
            user=user, recipe=recipe).exists()

        if request.method == 'POST':
            if favorite_exists:
                return Response(
                    {'detail': 'Рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not favorite_exists:
                return Response(
                    {'detail': 'Рецепта нет в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        in_cart = ShoppingCart.objects.filter(
            user=user, recipe=recipe).exists()

        if request.method == 'POST':
            if in_cart:
                return Response(
                    {'detail': 'Рецепт уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not in_cart:
                return Response(
                    {'detail': 'Рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_list = generate_shopping_list(user)

        if not shopping_list.strip():
            return Response(
                {'detail': 'Ваш список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = HttpResponse(shopping_list, content_type='text/plain')
        filename = f'shopping_cart_{user.username}.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_id = format(recipe.id, 'x')
        short_path = reverse('api:short-link', kwargs={'short_id': short_id})
        return Response(
            {'short-link': request.build_absolute_uri(short_path)},
            status=status.HTTP_200_OK
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter

    def list(self, request, *args, **kwargs):
        cache_key = f"ingredients_{request.query_params.get('name', '')}"
        data = cache.get(cache_key)

        if not data:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, timeout=60 * 60)
        return Response(data)


def short_link_redirect(request, short_id):
    try:
        recipe_id = int(short_id, 16)
        if recipe_id <= 0:
            raise ValueError
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return HttpResponseRedirect(f'/recipes/{recipe.id}/')
    except (ValueError, Http404):
        return HttpResponseRedirect('/404')
