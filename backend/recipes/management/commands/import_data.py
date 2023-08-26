import csv
import os

from django.core.management.base import BaseCommand

from foodgram_backend.settings import PARENT_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            nargs='?',
            default=os.path.join(PARENT_DIR, 'data', 'ingredients.csv'),
            help='Путь до CSV файла',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            for row in reader:
                mymodel = Ingredient()
                mymodel.name = row[0]
                mymodel.measurement_unit = row[1]
                mymodel.save()
