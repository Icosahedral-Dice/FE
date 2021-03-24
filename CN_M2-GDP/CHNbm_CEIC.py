#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 18:34:06 2021

@author: wanderer
"""

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

save_loc = '~/Desktop/hu/CN_M2-GDP/'
oecd = True # Set to False to hide OECD line

mpl.rcParams['font.family'] = 'Helvetica Neue'

# Data cleaning
data = pd.read_csv(save_loc + r'Name your insight.csv')
data = data.iloc[25:]
data.rename(columns = {'Unnamed: 0':'time'}, inplace = True)
data.rename(columns = {'CN: (DC)GDP Deflator':'GDP deflator'}, inplace = True)
data.rename(columns = {'CN: GDP':'GDP'}, inplace = True)
data.rename(columns = {'GDP Deflator: YoY':'GDP deflator YoY'}, inplace = True)
data.rename(columns = {'Money Supply M2: Seasonally Adjusted':'M2SA'}, inplace = True)
data.rename(columns = {'Money Supply M2':'M2'}, inplace = True)
data['time'] = data['time'].apply(lambda x: pd.to_datetime(str(x)))
data['time'] = pd.PeriodIndex(data['time'], freq = 'Q')
data = data.set_index('time')
data = data.astype(float)

# Pct changes (YoY)
df = pd.DataFrame()
df['GDP'] = 100*(data['GDP'].pct_change(4))    #YoY
df['Real GDP'] = df['GDP'] - data['GDP deflator YoY'] 
# 'GDP deflator YoY' is in fact GDP deflator GROWTH YoY.
df['M2'] = 100*(data['M2'].pct_change(4))
df['M2SA'] = 100*(data['M2SA'].pct_change(4))

if oecd:
    data_oecd = pd.read_pickle(save_loc + r'/CHNbm.pkl')
    data_oecd['time'] = data_oecd.index
    data_oecd['time'] = pd.PeriodIndex(data_oecd['time'], freq = 'Q')
    data_oecd = data_oecd.set_index('time')
    data_oecd = data_oecd.astype(float)
    df['OECD Broad Money'] = data_oecd['CHN']['MABMM301']['IXOBSA'].dropna()
    df['OECD Broad Money'] = 100*(df['OECD Broad Money'].pct_change(4,limit=1))

fig, axes = plt.subplots(1,1, figsize=(12,6), sharex=True)
df.plot(subplots=False, ax=axes, marker='o', ms=3)

# add titles
axes.set_title('Quarterly ' + 'M2, nominal and real GDP percentage change (YoY)',
             fontsize=14,
             fontweight='demi')

# add axis labels
axes.set_ylabel('% change', fontsize=12, fontweight='demi')
axes.set_xlabel('Date', fontsize=12, fontweight='demi')

axes.yaxis.set_major_formatter(mticker.PercentFormatter())

# bold up tick axes
axes.tick_params(axis='both', which='major', labelsize=11)


plt.savefig('CHNbm.png', dpi=300)
