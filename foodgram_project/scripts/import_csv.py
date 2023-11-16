import csv
import os

from foodgram_project.settings import BASE_DIR
from recipes.models import Ingredient

data_path = os.path.join(BASE_DIR, 'data', 'ingredients.csv')


def run():
    with open(data_path) as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            object = Ingredient()
            object.name = row[0]
            object.measurement_unit = row[1]
            data.append(object)
        Ingredient.objects.bulk_create(data)
    print('Finished!')

# python manage.py runscript import_csv
