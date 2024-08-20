import csv
from django.core.management.base import BaseCommand
from nutrition.models import NutritionInfo

class Command(BaseCommand):
    help = 'Import nutrition data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        self.stdout.write(f'Importing data from {csv_file_path}...')

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Ensure that no unexpected columns are in the CSV file
                if 'Item' in row and 'Calories' in row and 'Proteins' in row and 'Fats' in row and 'Sodium' in row and 'Fiber' in row and 'Carbs' in row and 'Sugar' in row:
                    NutritionInfo.objects.update_or_create(
                        item_name=row['Item'],
                        defaults={
                            'calories': float(row['Calories']),
                            'proteins': float(row['Proteins']),
                            'fats': float(row['Fats']),
                            'sodium': float(row['Sodium']),
                            'fiber': float(row['Fiber']),
                            'carbs': float(row['Carbs']),
                            'sugar': float(row['Sugar']),
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f"Imported {row['Item']}"))

        self.stdout.write(self.style.SUCCESS('Data import completed.'))
