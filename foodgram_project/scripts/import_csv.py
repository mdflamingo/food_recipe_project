import csv
from recipes.models import Ingredients


def run():
    with open('/Users/alexv/Dev/foodgram-project-react/data/ingredients.csv') as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            object = Ingredients()
            object.name = row[0]
            object.measure_unit = row[1]
            data.append(object)
        Ingredients.objects.bulk_create(data)
    print('Finished!')


# import csv
# from recipes.models import Ingredients


# def run():
#     file_path = '/Users/alexv/Dev/foodgram-project-react/data/ingredients.csv'
#     listoflists = list(csv.reader(open(file_path, 'r'), delimiter='\t'))
#     print(listoflists)
#     for row in listoflists:
#         Ingredients.objects.create(
#                 name=row[0],
#                 measure_unit=row[1])
        

# python manage.py runscript import_csv
