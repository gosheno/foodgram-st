from django.db.models import Sum
from .models import RecipeIngredient


def generate_shopping_list(user):
    ingredients = RecipeIngredient.objects.filter(
        recipe__in_shopping_carts__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        total_amount=Sum('amount')
    ).order_by('ingredient__name')

    shopping_list = "Список покупок:\n\n"
    for item in ingredients:
        shopping_list += (
            f"{item['ingredient__name']} - "
            f"{item['total_amount']} "
            f"{item['ingredient__measurement_unit']}\n"
        )

    shopping_list += "\nFoodgram - Ваш кулинарный помощник!"
    return shopping_list
