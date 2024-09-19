import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'ingredients.csv')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                Ingredient.objects.bulk_create(
                    (Ingredient(name=name, measurement_unit=unit)
                     for name, unit in csv.reader(f)),
                    ignore_conflicts=True
                )
            self.stdout.write(
                self.style.SUCCESS('Successfully added ingredients!')
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except csv.Error as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV file: {e}'))
