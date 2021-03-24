#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 08:09:38 2021

@author: wanderer
"""

# https://github.com/LenkaV/CIF/blob/develop/examples/CI_minimalPipeline.ipynb

# import os
from cif import cif
import pandas as pd
import datetime


import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# print(os.environ['X13PATH'])
# only for seasonal adjustment

mpl.rcParams['font.family'] = 'Helvetica Neue'
save_loc = '~/Desktop/hu'

redownloaddata = True

if redownloaddata:
    country = 'CHN' # Select target country
    
    bw = False # True for black and white visualisations
    
    saveData = False # Save the original data sets if True
    
    strDate = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    
    #outputDir = os.path.join('plots_' + country + '_' + strDate)
    #os.makedirs(outputDir, exist_ok = True)
    
    data_all, subjects_all, measures_all = cif.createDataFrameFromOECD(countries = [country], dsname = 'MEI', frequency = 'Q',
                                                                        subject = ['NAEXCP01','MABMM301'],
                                                                        measure = ['STSA','IXOBSA'])
    
    #data_rs, subjects_rs, measures_rs = cif.createDataFrameFromOECD(countries = [country], dsname = 'QNA', subject = ['B1_GE'], frequency = 'Q')
    
    print('Downloaded MEI data set size: %d x %d' % (data_all.shape[0], data_all.shape[1]))
    # print('Downloaded reference data set size: %d x %d' % (data_rs.shape[0], data_rs.shape[1]))
    
    '''
    if saveData:
        # Save the data
        data_all.to_csv(os.path.join(outputDir, 'data_all.csv'))
        subjects_all.to_csv(os.path.join(outputDir, 'subjects_all.csv'))
        measures_all.to_csv(os.path.join(outputDir, 'measures_all.csv'))
        data_rs.to_csv(os.path.join(outputDir, 'data_rs.csv'))
        subjects_rs.to_csv(os.path.join(outputDir, 'subjects_rs.csv'))
        measures_rs.to_csv(os.path.join(outputDir, 'measures_rs.csv'))
    '''
    # print(data_all)
    
    data_all['time'] = data_all.index
    data_all['time'] = pd.PeriodIndex(data_all['time'], freq = 'Q')
    data_all = data_all.set_index('time')

    
    deflator = pd.read_csv(save_loc + r'/GDP Deflator YoY Quarterly China.csv')
    deflator = deflator.iloc[25:]
    deflator.rename(columns = {'Unnamed: 0':'time'}, inplace = True)
    deflator.rename(columns = {'GDP Deflator: YoY: Quarterly: China':'GDP deflator'}, inplace = True)
    deflator['time'] = deflator['time'].apply(lambda x: pd.to_datetime(str(x)))
    deflator['time'] = pd.PeriodIndex(deflator['time'], freq = 'Q')
    deflator = deflator.set_index('time')
    
    # Convert YOY deflator to constant price (2015Q1) deflator
    deflator['GDP deflator'] = deflator['GDP deflator'].astype(float)
    deflator = deflator['GDP deflator'].apply(lambda x:1 + x/100)
    deflator = deflator.cumprod()
    deflator = deflator/(deflator['2015Q1'])
    
    deflator.to_pickle(save_loc + r'/CHNdefl.pkl')  
    data_all.to_pickle(save_loc + r'/CHNbm.pkl')

    
deflator = pd.read_pickle(save_loc + r'/CHNdefl.pkl')
data_all = pd.read_pickle(save_loc + r'/CHNbm.pkl')
data = pd.DataFrame({'Broad money' : []})
data['Broad money'] = data_all['CHN']['MABMM301']['IXOBSA']
data['Nominal GDP'] = data_all['CHN']['NAEXCP01']['STSA']
data = pd.concat([data, deflator], axis=1)
data['Real GDP'] = data['Nominal GDP'] * data['GDP deflator']
pltdata = data.drop('GDP deflator', axis=1)

# Same period last year
pltdata = pltdata.pct_change(periods = 4)
pltdata = 100*pltdata


# Graphing!
fig, axes = plt.subplots(1,1, figsize=(12,6), sharex=True)
pltdata.plot(subplots=False, ax=axes, marker='o', ms=3)

# add titles
axes.set_title('Quarterly ' + 'M3, nominal and real GDP percentage change',
             fontsize=14,
             fontweight='demi')

# add axis labels
axes.set_ylabel('% change\n(Annualized)', fontsize=12, fontweight='demi')
axes.set_xlabel('Date', fontsize=12, fontweight='demi')

axes.yaxis.set_major_formatter(mticker.PercentFormatter())

# bold up tick axes
axes.tick_params(axis='both', which='major', labelsize=11)


plt.savefig('CHNbm.png', dpi=300)
