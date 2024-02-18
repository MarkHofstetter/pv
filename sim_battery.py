'''
Summe Verbrauch und feedin

Messzeitpunkt;Einspeisung (kWh) Strom 00100137997;Qualität Strom 00100137997;Verbrauch (kWh) Strom 00021228596;Qualität Strom 00021228596;
01.01.2023 00:15;;;;;
10.08.2023 07:00;0,000000;G;0,092000;G;

'''
import csv
import numpy
from tabulate import tabulate
import argparse

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


parser = argparse.ArgumentParser(description="Process a CSV file.")
parser.add_argument('--csv', type=str, required=True, help='The name of the CSV file to process.')
parser.add_argument('--capacity', type=float, required=True, help='Capacity of battery')

args = parser.parse_args()


saved = 0
def convert_cell(cell):
    if cell == '':
        ret = 0
    else:
        ret = float(cell.replace (',', '.'))
    return ret

def movingaverage(interval, window_size):
    window= numpy.ones(int(window_size))/float(window_size)
    return numpy.convolve(interval, window, 'same')


table = []

with open(args.csv) as csvfile:
    data = list(csv.reader(csvfile, delimiter=';'))
#print(data[22495][1])

date_format = "%d.%m.%y %H:%M"
feedin_col = 1
consumption_col = 3


# Roman
# date_format = "%d.%m.%Y %H:%M"
# feedin_col = 3
# consumption_col = 1

sum = {}
dates = []
sum['pv'] = []
sum['net'] = []
sum['bat'] = []
sum['agg_feedin'] = []
sum['agg_sim_feedin'] = []
sum['agg_consumption'] = []
sum['agg_sim_consumption'] = []
sum['agg_saved'] = []
sum['feedin'] = 0
sum['consumption'] = 0
sum['sim_consumption'] = 0
sum['sim_feedin'] = 0

bat_capacity = args.capacity
bat_charge = 0
bat_consumed = 0
direct_use = 0
for row in data[1:]:
    
    feedin = convert_cell(row[feedin_col])
    consumption = convert_cell(row[consumption_col])
    sum['feedin'] += feedin
    sum['consumption'] += consumption
    error_line = ''
    
    '''
    if net_usage is positive more is consumed dann produced, so energy is
    taken either from the battery or the net
    '''
    net_usage = consumption - feedin
    
    if net_usage > 0 and bat_charge > 0:       
        real_consumption = net_usage
        if bat_charge - net_usage < 0:            
            real_consumption =  bat_charge
            error_line = f"uc {real_consumption}  {net_usage}"      
            sum['sim_consumption'] += net_usage - real_consumption 
        bat_charge -= real_consumption        
        bat_consumed += real_consumption
    elif net_usage > 0 and bat_charge <= 0:
        sum['sim_consumption'] += net_usage      
    # charge battery           
    elif net_usage <= 0 and bat_charge <= bat_capacity:
        real_charge = net_usage
        if bat_charge - net_usage >= bat_capacity:
            real_charge =  bat_capacity - bat_charge
            error_line = f"oc {bat_charge} {net_usage} {real_charge} {-net_usage - real_charge}"            
            sum['sim_feedin'] += (-net_usage - real_charge)
            real_charge *= -1                          
            direct_use += -real_charge         
        bat_charge += -real_charge
        saved += -real_charge
    # battery full => deliver to net
    elif net_usage <= 0 and bat_charge > bat_capacity:        
        error_line = f"to net {-net_usage}"
        sum['sim_feedin'] += -net_usage
    else: 
        error_line = 'X'
        print("XXX fehler")
    
    dates.append(row[0])
    sum['pv'].append(-feedin)
    sum['net'].append(consumption)
    sum['bat'].append(bat_charge)
    sum['agg_saved'].append(saved)
    sum['agg_feedin'].append(sum['feedin'])
    sum['agg_sim_feedin'].append(sum['sim_feedin'])
    sum['agg_consumption'].append(sum['consumption'])
    sum['agg_sim_consumption'].append(sum['sim_consumption'])

    table.append({'net_usage': net_usage, 
                  'feedin': feedin, 
                  'consumption': consumption, 
                  'sim_feedin': sum['sim_feedin'], 
                  'sim_consumption': sum['sim_consumption'], 
                  'sum feedin': sum['feedin'], 
                  'sum consumption': sum['consumption'], 
                  'bat_charge': bat_charge,
                  'saved': saved,
                  'error_line': error_line
                  })
    


dates = pd.to_datetime(dates, format=date_format)

plt.figure(figsize=(10, 20))
font = { 'size'   : 5}

plt.rc('font', **font)
# fig, ax = plt.subplots(2, 1, sharex=True)
fig, ax = plt.subplots(3, sharex=True)

linewidth=0.3

ax[0].plot(dates, sum['pv'], label='PV Einlieferung', linewidth=linewidth)
ax[0].plot(dates, sum['net'], label='Netz', linewidth=linewidth)
pv_av = movingaverage(sum['pv'], 96)
ax[0].plot(dates, pv_av, label='PV avg', linewidth=linewidth*2)
net_av = movingaverage(sum['net'], 96)
ax[0].plot(dates, net_av, label='Netz avg', linewidth=linewidth*2)

bat_av = movingaverage(sum['bat'], 96)
ax[1].plot(dates, sum['bat'], label='Ladezustand', linewidth=linewidth)
ax[1].plot(dates, bat_av, label='Ladezustand avg', linewidth=linewidth*2)
ax[1].set_ylim(0, bat_capacity * 1.1)

ax[0].xaxis.set_major_locator(mdates.MonthLocator())
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))

ax[2].plot(dates, sum['agg_saved'], label='From Battery', linewidth=linewidth)
ax[2].plot(dates, sum['agg_feedin'], label='PV to net', linewidth=linewidth)
ax[2].plot(dates, sum['agg_sim_feedin'], label='PV to net simulated', linewidth=linewidth)
ax[2].plot(dates, sum['agg_consumption'], label='From Net', linewidth=linewidth)
ax[2].plot(dates, sum['agg_sim_consumption'], label='From Net simulated', linewidth=linewidth)
# ax[2].xaxis.label.set_size(2)
# ax[2].plot(dates, bat_av, label='Ladezustand avg', linewidth=linewidth*2)
# ax[2].set_ylim(0, bat_capacity * 1.1)


# Improve formatting
plt.gcf().autofmt_xdate()  # Auto formats the x-axis labels to fit them better
ax[0].legend(loc="best")
ax[1].legend(loc="best")
ax[2].legend(loc="best")

fontsize=2
plt.rc('font', size=fontsize)
plt.rc('axes', titlesize=fontsize, labelsize=fontsize, )
plt.xlabel('Datum')
plt.setp(ax[0], ylabel='kWh/15min')
plt.setp(ax[1], ylabel='kWh', )
plt.setp(ax[2], ylabel='kWh', )

plt.savefig('fig.png', dpi=300)

# print(tabulate(table, headers="keys", tablefmt="grid"))    
print("feedin %.2f - %.2f" % (sum['feedin'], sum['sim_feedin']))
print("consumption   %.2f - %.2f" % (sum['consumption'], sum['sim_consumption']))
print("netto - sim netto - saved %.2f - %.2f - %.2f - %.2f" % (sum['feedin']-sum['consumption'], sum['sim_feedin']-sum['sim_consumption'], saved, bat_consumed))
print("Ladezustand %.2f  - direct use %.2f " % (bat_charge, direct_use ))

