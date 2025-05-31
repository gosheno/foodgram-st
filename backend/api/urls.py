from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from recipes.views import RecipeViewSet, IngredientViewSet, short_link_redirect
router = DefaultRouter()

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')

app_name = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('rec/<str:short_id>/', short_link_redirect, name='short-link'),
]
