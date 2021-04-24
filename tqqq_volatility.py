#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 21:23:24 2021

@author: rdchlmtr
"""
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_market_calendars as mcal
import matplotlib.dates as mdates
import datetime
import seaborn as sns

sns.set_theme()
plt.close('all')

#%% parameters

start_date = '2021-01-01'
end_date = '2022-01-01'

# parameters for tqqq
par1 = 5
par2 = 35
par3 = 5

# parameters for vxn
par4 = 12
par5 = 26
par6 = 9

start_money = 10000

#%% gathering, analyzing data

tqqq = yf.download(tickers='TQQQ', start=start_date, end=end_date)
vxn = yf.download(tickers='^VXN', start=start_date, end=end_date)

# something breaks if you don't do this nyse stuff below, but I don't remember what. Something about no trading on weekends, maybe, but someone on stackoverflow said you need it and it works...

nyse = mcal.get_calendar('NYSE')
nyse_schedule = nyse.schedule(start_date=tqqq.index[0], end_date=tqqq.index[-1])
nyse_dti = mcal.date_range(nyse_schedule, frequency='1D').tz_convert(nyse.tz.zone)

# reframe the data with new index
t = pd.DataFrame({'Close':tqqq.Close.values, 'Open':tqqq.Open.values}, index=nyse_dti)
v = pd.DataFrame({'Close':vxn.Close.values, 'Open':vxn.Open.values}, index=nyse_dti)

# calculating MACD
exp1 = t.Close.ewm(span=par1, adjust=False).mean()
exp2 = t.Close.ewm(span=par2, adjust=False).mean()
t['macd'] = exp1-exp2
t['exp3'] = t.macd.ewm(span=par3, adjust=False).mean()
t['good'] = t.macd > t.exp3
t['zeros'] = np.zeros(len(t.macd))

exp1 = v.Close.ewm(span=par4, adjust=False).mean()
exp2 = v.Close.ewm(span=par5, adjust=False).mean()
v['macd'] = exp1-exp2
v['exp3'] = v.macd.ewm(span=par6, adjust=False).mean()
v['good'] = v.macd < v.exp3
v['zeros'] = np.zeros(len(v.macd))

# good = t.good
good = (t.good & v.good)

# theres probably a better way to do all of the below
# i wanted two columns of dates, the first column is the dates you should buying, the second column is dates you should sell, so each row brackets the "good" periods
# this makes the green bands in the figure easier to map out
buy = np.where(np.diff(good ))[0] # record indices where (t.good & v.good) condition changes
if len(buy) % 2 != 0: # if you are currently in a "good" period, then the final bracket is unclosed
    buy = np.append(buy, -1) # this just adds the final index to close the last bracket
    action = 'BUY' # this just tells you if we're currently (i.e. on the end_date) in a BUY or SELL scenario, I was using it in the figure title, but not anymore
else:
    action = 'SELL'
    
buy = buy.reshape((len(buy)//2,2)) # reshape the array so buy dates in first column, sell dates in second column
buy_times = np.array(t.index)[buy] # convert to actual dates instead of indices
holds = (buy_times[:,1] - buy_times[:,0]) / datetime.timedelta(days=1) # how long each hold is
avg_hold_time = np.mean(holds)

#%% backtesting model

open_price = t.Open.values # we buy at today's price, algorithm uses yesterdays close price
close_price = t.Close.values
balance = np.zeros(len(t))
shares = np.zeros(len(t))
value = np.zeros(len(t))
total = np.zeros(len(t))

balance[0] = start_money
total[0] = start_money


for i in range(1, len(t)):
    if good[i-1] > good[i-2]: # if condition changes from bad to good
        shares[i] = balance[i-1] // open_price[i] # how many shares can we buy at today's price with yesterday's account balance
        balance[i] = balance[i-1] % open_price[i] # remainder in account after buying shares
    elif good[i-1] == good[i-2]: # if condition doesn't change
        shares[i] = shares[i-1]
        balance[i] = balance[i-1]
    elif good[i-1] < good[i-2]: # if condition changes from good to bad
        shares[i] = 0
        balance[i] = shares[i-1] * open_price[i] + balance[i-1]
    value[i] = shares[i] * close_price[i]
    total[i] = value[i] + balance[i]
    
model = pd.DataFrame({'balance':balance,'shares':shares,'value':value,'total':total}, index=nyse_dti)
# model['worth'] = model.value + model.balance # total worth each day (value of shares + value in account)
initial = start_money//open_price[0] # how many shares could we have bought on day 1
model['hodl'] = close_price*initial + start_money - open_price[0]*initial # if stock was bought on day one and held

algo_gain = model.total[-1] - model.total[0] # net gain over time domain
hodl_gain = model.hodl[-1] - model.hodl[0]

net = model.total[-1] - model.hodl[-1] # improvement of model over hodling
print('{:.0f}'.format(total[-1])) # just some visual feedback

#%%


fig1 = plt.Figure(figsize=(11,8))


ax1 = plt.subplot(4, 1, 1)
plt.plot(t.Close, '-g', label='TQQQ')
ax1b = ax1.twinx()
plt.plot([], [], '-g', label ='TQQQ')
plt.plot(v.Close, '-r', label='VXN')
for i in range(len(buy_times)):
    ax1.axvspan(buy_times[i,0], buy_times[i,1], facecolor='g', alpha=0.2)
plt.legend(loc=2)
ax1b.xaxis.set_major_formatter(mdates.DateFormatter(''))
plt.title('ALGO Gain: ${:,.2f}\nHODL Gain: ${:,.2f}\nAvg. Hold Time: {:.1f} days'.format(algo_gain, hodl_gain, avg_hold_time))


ax2 = plt.subplot(4, 1, 2)
plt.plot(t.macd, label='TQQQ MACD')
plt.plot(t.exp3, label='TQQQ Signal')
plt.fill_between(t.index, t.zeros, 2*(t.macd-t.exp3), color='gray', label='Hist')
for i in range(len(buy_times)):
    ax2.axvspan(buy_times[i,0], buy_times[i,1], facecolor='g', alpha=0.2)  
ax2.grid()
plt.legend(loc=2)
ax2.xaxis.set_major_formatter(mdates.DateFormatter(''))


ax3 = plt.subplot(4, 1, 3)
plt.plot(v.macd, label='VXN MACD')
plt.plot(v.exp3, label='VXN Signal')
plt.fill_between(v.index, v.zeros, 2*(v.macd-v.exp3), color='gray', label='Hist')
for i in range(len(buy)):
    ax3.axvspan(buy_times[i,0], buy_times[i,1], facecolor='g', alpha=0.2)  
ax2.grid()
plt.legend(loc=2)
ax3.xaxis.set_major_formatter(mdates.DateFormatter(''))

ax4 = plt.subplot(4,1,4)
plt.plot(model.hodl, label='HODL')
plt.plot(model.total, label='ALGO')
plt.legend(loc=2)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
    

plt.subplots_adjust(hspace = .0001)


plt.show()
# plt.savefig('/Users/rdchlmtr/tqqq.png')




