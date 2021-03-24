#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 18:49:46 2021

@author: wanderer
"""

### Housekeeping ###
import pandas as pd
import pandas_datareader.data as web

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import seaborn as sns
sns.set_style('white', {"xtick.major.size": 2, "ytick.major.size": 2})
flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71","#f4cae4"]
sns.set_palette(sns.color_palette(flatui,7))

from dateutil.relativedelta import relativedelta

save_loc = '~/Desktop/hu'

redownload = True
if redownload:
    f1 = 'USREC' # recession data from FRED
    f2 = 'M2SL' # M2 from FRED
    
    start = pd.to_datetime('1959-12-01')
    end = pd.to_datetime('2020-12-31')
    
    M2 = web.DataReader([f2], 'fred', start, end)
    data_line = M2.pct_change()
    data_line = data_line.apply(lambda x: 12*x)
    
    data_shade = web.DataReader([f1], 'fred', start, end)
    data = data_shade.join(data_line, how='outer').dropna()
    
    data.to_pickle(save_loc + r'/M2SL.pkl')


data = pd.read_pickle(save_loc + r'/M2SL.pkl')

# recessions are marked as 1 in the data
recs = data.query('USREC==1')

plot_cols = ['M2SL']

mpl.rcParams['font.family'] = 'Helvetica Neue'

fig, axes = plt.subplots(1,1, figsize=(12,6), sharex=True)
data[plot_cols].plot(subplots=True, ax=axes, marker='o', ms=3)

col = plot_cols
ax = axes

for month in recs.index:
    ax.axvspan(month, month+ relativedelta(months=+1),
               color=sns.xkcd_rgb['grey'], alpha=0.5)

# lets add horizontal zero lines
ax.axhline(0, color='k', linestyle='-', linewidth=1)

# add titles
ax.set_title('Monthly ' + 'M2 percentage change' +
             ' \nRecessions Shaded Gray',
             fontsize=14,
             fontweight='demi')

# add axis labels
ax.set_ylabel('% change\n(Annualized)', fontsize=12, fontweight='demi')
ax.set_xlabel('Date', fontsize=12, fontweight='demi')

# upgrade axis tick labels
yticks = ax.get_yticks()
ax.yaxis.set_major_locator(mticker.FixedLocator(yticks))
ax.set_yticklabels(['{:3.1f}%'.format(x*100) for x in yticks]);
dates_rng = pd.date_range(data.index[0], data.index[-1], freq='24M')
plt.xticks(dates_rng, [dtz.strftime('%Y-%m') for dtz in dates_rng],
           rotation=45)


# bold up tick axes
ax.tick_params(axis='both', which='major', labelsize=11)

# add cool legend
ax.legend(loc='upper left', fontsize=11, labels=['M2'],
          frameon=True).get_frame().set_edgecolor('blue')  

plt.savefig('M2SL_recession.png', dpi=300)


