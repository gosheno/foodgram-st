from django.db.models import Sum
from django.core.cache import cache

from .models import RecipeIngredient


def generate_shopping_list(user):
    cache_key = f"shopping_list_{user.id}"
    shopping_list = cache.get(cache_key)
    
    if not shopping_list:
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=user
        ).select_related('ingredient').values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list = ["Список покупок:\n"]
        shopping_list.extend(
            f"{item['ingredient__name']} - {item['total_amount']} {item['ingredient__measurement_unit']}"
            for item in ingredients
        )
        shopping_list.append("\nFoodgram - Ваш кулинарный помощник!")
        shopping_list = '\n'.join(shopping_list)
        cache.set(cache_key, shopping_list, timeout=60*60)  # 1 час
    
    return shopping_list