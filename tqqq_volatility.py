import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_market_calendars as mcal
import matplotlib.dates as mdates
import seaborn as sns

sns.set_theme()
plt.close('all')
#%% parameters

start_date = '2012-01-01'
end_date = '2022-01-01'

par1 = 2
par2 = 18
par3 = 2

start_money = 1000


#%% gathering, analyzing data

tqqq = yf.download(tickers='TQQQ', start=start_date, end=end_date)
vxn = yf.download(tickers='^VXN', start=start_date, end=end_date)

# this nyse stuff makes the X-axis in the figures better, since no trading on weekends

nyse = mcal.get_calendar('NYSE')
nyse_schedule = nyse.schedule(start_date=tqqq.index[0], end_date=tqqq.index[-1])
nyse_dti = mcal.date_range(nyse_schedule, frequency='1D').tz_convert(nyse.tz.zone)

t = pd.DataFrame({'Close':tqqq.Close.values}, index=nyse_dti)
v = pd.DataFrame({'Close':vxn.Close.values}, index=nyse_dti)


exp1 = t.Close.ewm(span=par1, adjust=False).mean()
exp2 = t.Close.ewm(span=par2, adjust=False).mean()
t['macd'] = exp1-exp2
t['exp3'] = t.macd.ewm(span=par3, adjust=False).mean()
t['good'] = t.macd > t.exp3
t['zeros'] = np.zeros(len(t.macd))

exp1 = v.Close.ewm(span=par1, adjust=False).mean()
exp2 = v.Close.ewm(span=par2, adjust=False).mean()
v['macd'] = exp1-exp2
v['exp3'] = v.macd.ewm(span=par3, adjust=False).mean()
v['good'] = v.macd < v.exp3
v['zeros'] = np.zeros(len(v.macd))


buy = np.where(np.diff(t.good & v.good))[0] # both indicators must be good
if len(buy) % 2 != 0: 
    buy = np.append(buy, -1)
    action = 'BUY'
else:
    action = 'SELL'
    
buy = buy.reshape((len(buy)//2,2)) # making a list of buy and sell times
buy_times = np.array(t.index)[buy]
holds = buy_times[:,1] - buy_times[:,0] # how long each hold is
avg_hold_time = np.mean(holds)
days = avg_hold_time.total_seconds() /60/60/24

#%% backtesting model

price = tqqq.Open.values # we buy at today's price, algorithm uses yesterdays close price
balance = np.zeros(len(t))
shares = np.zeros(len(t))
value = np.zeros(len(t))
good = t.good & v.good
balance[0] = start_money


for i in range(1, len(t)):
    if good[i] > good[i-1]: # if condition changes from bad to good
        new_shares = balance[i-1] // price[i]
        new_balance = balance[i-1] % price[i]
        shares[i] = new_shares
        balance[i] = new_balance
    elif good[i] == good[i-1]: # if condition doesn't change
        shares[i] = shares[i-1]
        balance[i] = balance[i-1]
    elif good[i] < good[i-1]: # if condition changes from good to bad
        new_shares = 0
        new_balance = shares[i-1] * price[i]
        shares[i] = new_shares
        balance[i] = balance[i-1] + new_balance
    value[i] = shares[i] * price[i]
    
model = pd.DataFrame({'value':value,'balance':balance}, index=nyse_dti)
model['worth'] = model.value + model.balance # net worth each day
initial = start_money//price[0]
model['hodl'] = price*initial + start_money - price[0]*initial # if stock was bought on day one and held

algo_gain = model.worth[-1] - model.worth[0]
hodl_gain = model.hodl[-1] - model.hodl[0]

net = model.worth[-1] - model.hodl[-1]
print('{:.0f}'.format(net))

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
plt.title('ALGO Gain: ${:,.2f}\nHODL Gain: ${:,.2f}\nAvg. Hold Time: {:.1f} days'.format(algo_gain, hodl_gain, days))


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
plt.plot(model.worth, label='ALGO')
plt.legend(loc=2)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
    

plt.subplots_adjust(hspace = .0001)


plt.show()
# plt.savefig('/Users/rdchlmtr/tqqq.png')




