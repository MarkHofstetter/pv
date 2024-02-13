'''
Summe Verbrauch und Einspeisung

Messzeitpunkt;Einspeisung (kWh) Strom 00100137997;Qualität Strom 00100137997;Verbrauch (kWh) Strom 00021228596;Qualität Strom 00021228596;
01.01.2023 00:15;;;;;
10.08.2023 07:00;0,000000;G;0,092000;G;

'''
import csv
import numpy
summe = 0
with open('Jahresbilanz 2023.csv') as csvfile:
    data = list(csv.reader(csvfile, delimiter=';'))
#print(data[22495][1])
for row in data[1:]:
    fixed = row[1].replace (',', '.')
    if fixed == '':
        fixed = 0
    summe = summe + float(fixed)
print(summe)