from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _  # Импорт функции перевода


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = _('Рецепты')
