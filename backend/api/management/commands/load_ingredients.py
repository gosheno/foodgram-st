import json
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from JSON file'

    def handle(self, *args, **kwargs):
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../../../data/ingredients.json'
        ))

        with open(file_path, 'r', encoding='utf-8') as f:
            ingredients = json.load(f)
            ingredient_objects = [
                Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                for item in ingredients
            ]
            Ingredient.objects.bulk_create(
                ingredient_objects, ignore_conflicts=True
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {len(ingredient_objects)} ingredients'
            )
        )
