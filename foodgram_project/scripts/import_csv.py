import csv

from recipes.models import Ingredient


def run():
    with open('foodgram_project/data/ingredients.csv') as file:
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
