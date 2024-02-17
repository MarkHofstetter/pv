'''
Summe Verbrauch und Einspeisung

Messzeitpunkt;Einspeisung (kWh) Strom 00100137997;Qualität Strom 00100137997;Verbrauch (kWh) Strom 00021228596;Qualität Strom 00021228596;
01.01.2023 00:15;;;;;
10.08.2023 07:00;0,000000;G;0,092000;G;

'''
import csv
import numpy
summe = 0
sum_einspeisung = 0
sum_verbrauch = 0

sim_verbrauch = 0
sim_einspeisung = 0

bat_capacity = 5
bat_charge = 0

saved = 0
def convert_cell(cell):
    if cell == '':
        ret = 0
    else:
        ret = float(cell.replace (',', '.'))
    return ret


with open('test-pv.csv') as csvfile:
    data = list(csv.reader(csvfile, delimiter=';'))
#print(data[22495][1])
for row in data[1:]:
    einspeisung = convert_cell(row[1])
    verbrauch = convert_cell(row[3])
    sum_einspeisung += einspeisung
    sum_verbrauch += verbrauch
    net_usage = verbrauch - einspeisung
    if net_usage > 0 and bat_charge > 0:
        bat_charge -= net_usage
    elif net_usage <= 0 and bat_charge < bat_capacity:
        bat_charge += -net_usage
        saved += net_usage
    elif net_usage > 0 and bat_charge <= 0:
        sim_verbrauch += net_usage
    elif net_usage <= 0 and bat_charge > bat_capacity:
        sim_einspeisung += -net_usage
    else: 
        print("XXX fehler")
    
    print( einspeisung, verbrauch, sum_einspeisung, sum_verbrauch, net_usage, bat_charge)           

    
print("Einspeisung %.2f - %.2f" % (sum_einspeisung, sim_einspeisung))
print("Verbrauch   %.2f - %.2f" % (sum_verbrauch, sim_verbrauch))
print("netto - sim - saved %.2f - %.2f - %.2f" % (sum_einspeisung-sum_verbrauch, sim_einspeisung-sim_verbrauch, saved))
print("Ladezustand %.2f" % (bat_charge))


