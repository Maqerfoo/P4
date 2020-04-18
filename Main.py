# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020

@author: jakob
"""

from Demandgenerator import create_demand_year
import math

avg_demand_week0 = {'Lakrids 1' : 8000, 'Lakrids 2' : 8000, 'Lakrids 3' : 8000,
          'Lakrids 4' : 8000, 'Chocolate A' : 15360, 'Chocolate B' : 15360, 
          'Chocolate C' : 15360, 'Chocolate D' : 15360, 'Chocolate E' : 15360,
          'Crispy Caramel' : 12800, 'Blackberry & Dark' : 12800, 
          'Twisted Banana' : 12800, 'Vanilla Mango' : 12800}   


demand2020 = create_demand_year(2020, avg_demand_week0, mean=0.15, sd=0.025)


#we can only produce integer number of batches of quantity 1850. So we produce
#lowest integer, greater than batch quantity. Then we need to adjust for rollover
#from previous weeks production

lakrids = demand2020.loc[ : , demand2020.columns.str.startswith("Lakrids")]
chocolate_adjusted_rollover = demand2020.loc[ : , demand2020.columns.str.startswith("Lakrids") == False] 
chocolate_batch = chocolate_adjusted_rollover / 1875
chocolate_batch_produced = chocolate_batch.copy()
for i in range(len(chocolate_batch)):
    if i == len(chocolate_batch)-1:
        break
    for x in range(len(chocolate_batch.columns)):
        chocolate_batch_produced.iloc[i, x] = math.ceil(chocolate_batch.iloc[i, x])
        chocolate_adjusted_rollover.iloc[i+1, x] = chocolate_adjusted_rollover.iloc[i+1, x] - (chocolate_batch_produced.iloc[i,x] * 1875 - chocolate_adjusted_rollover.iloc[i,x])
for i in range(len(chocolate_batch_produced.columns)):
    chocolate_batch_produced.iloc[-1, i] = math.ceil(chocolate_batch_produced.iloc[-1, i])


