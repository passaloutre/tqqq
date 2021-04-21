#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 15:47:03 2021

@author: rdchlmtr
"""

# -*- coding: utf-8 -*-

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_market_calendars as mcal
import matplotlib.dates as mdates
import seaborn as sns

sns.set_theme()
plt.close('all')
#%%

start_date = '2021-01-01'
end_date = '2022-01-01'

par1 = np.arange(2,5)
par2 = np.arange(15,30)
par3 = np.arange(2,5)
net = np.zeros(len(par1)*len(par2)*(len(par3)))
output = np.zeros((5,len(net)))
#%%

tqqq = yf.download(tickers='TQQQ', start=start_date, end=end_date)
vix = yf.download(tickers='^VXN', start=start_date, end=end_date)

nyse = mcal.get_calendar('NYSE')
nyse_schedule = nyse.schedule(start_date=tqqq.index[0], end_date=tqqq.index[-1])
nyse_dti = mcal.date_range(nyse_schedule, frequency='1D').tz_convert(nyse.tz.zone)

t = pd.DataFrame({'Close':tqqq.Close.values}, index=nyse_dti)
v = pd.DataFrame({'Close':vix.Close.values}, index=nyse_dti)

n = 0

for x in par1:
    for y in par2:
        for z in par3:

            exp1 = t.Close.ewm(span=x, adjust=False).mean()
            exp2 = t.Close.ewm(span=y, adjust=False).mean()
            t['macd'] = exp1-exp2
            t['exp3'] = t.macd.ewm(span=z, adjust=False).mean()
            t['good'] = t.macd > t.exp3
            t['zeros'] = np.zeros(len(t.macd))
            
            
            exp1 = v.Close.ewm(span=x, adjust=False).mean()
            exp2 = v.Close.ewm(span=y, adjust=False).mean()
            v['macd'] = exp1-exp2
            v['exp3'] = v.macd.ewm(span=z, adjust=False).mean()
            v['good'] = v.macd < v.exp3
            v['zeros'] = np.zeros(len(v.macd))
            
            
            buy = np.where(np.diff(t.good & v.good))[0]
            if len(buy) % 2 != 0: 
                buy = np.append(buy, -1)
                action = 'BUY'
                condition= 'BULL'
            else:
                action = 'SELL'
                condition = 'BEAR'
                
            buy = buy.reshape((len(buy)//2,2))
            buy_times = np.array(t.index)[buy]
            
            price = tqqq.Open.values
            balance = np.zeros(len(t))
            shares = np.zeros(len(t))
            value = np.zeros(len(t))
            good = t.good & v.good
            balance[0] = 1000
            
            
            for i in range(1, len(t)):
                if good[i] > good[i-1]:
                    new_shares = balance[i-1] // price[i]
                    new_balance = balance[i-1] % price[i]
                    shares[i] = new_shares
                    balance[i] = new_balance
                elif good[i] == good[i-1]:
                    shares[i] = shares[i-1]
                    balance[i] = balance[i-1]
                elif good[i] < good[i-1]:
                    new_shares = 0
                    new_balance = shares[i-1] * price[i]
                    shares[i] = new_shares
                    balance[i] = balance[i-1] + new_balance
                value[i] = shares[i] * price[i]
                
            model = pd.DataFrame({'value':value,'balance':balance}, index=nyse_dti)
            model['worth'] = model.value + model.balance
            initial = 1000//price[0]
            model['hodl'] = price*initial + 1000 - price[0]*initial
            
            net[n] = model.worth[-1] - model.hodl[-1]
            output[0,n] = x
            output[1,n] = y
            output[2,n] = z
            output[3,n] = len(buy_times)
            output[4,n] = net[n]
            # print('{:.0f}'.format(net[n]))
            n = n + 1
            
dat = pd.DataFrame(output.T, columns=['P1', 'P2', 'P3', 'Buys', 'Net'])


#%%
fig1 = plt.figure()

ax1 = plt.subplot(4,1,1)
sns.boxplot(x=dat.P1, y=dat.Net, data=dat)

ax1 = plt.subplot(4,1,2)
sns.boxplot(x=dat.P2, y=dat.Net, data=dat)

ax1 = plt.subplot(4,1,3)
sns.boxplot(x=dat.P3, y=dat.Net, data=dat)

ax1 = plt.subplot(4,1,4)
sns.boxplot(x=dat.P1, y=dat.Buys, data=dat)