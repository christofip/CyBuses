import pandas as pd
import csv

#df = pd.read_csv('/Users/pchristofi/Documents/CyBuses/data/static/stops.csv', delimiter=';', encoding='utf-8-sig')


#print(df[df['code'] == 1441])

from dbfread import DBF

table = DBF('/Users/pchristofi/Documents/CyBuses/data/static/routes/routes.dbf')
print("Fields in routes.dbf:")
for field in table.fields:
    print(field.name)