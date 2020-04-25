# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 11:52:12 2020

@author: jakob
"""
import math
from scipy.stats import norm

#we can only produce integer number of batches of quantity 1875. So we produce
#lowest integer, greater than batch quantity. Then we need to adjust for rollover
#from previous weeks production

def batches_produced(demand, mean, sd):
    chocolate = demand.loc[ : , demand.columns.str.startswith("Lakrids") == False] 
    liquorice_produced = demand.loc[ : , demand.columns.str.startswith("Lakrids")] 
    chocolate_rollover = chocolate.copy()
    for col in chocolate_rollover.columns:
        chocolate_rollover[col].values[:] = 0
    #the chocolate output from one individual batch is stochastic - the mean of all batches is 1875
    chocolate_batch_produced = chocolate_rollover.copy()
    batch_quantity_save = chocolate_rollover.copy()
    for i in range(len(chocolate_batch_produced)):
        #last week generates no rollover
        if i == len(chocolate_batch_produced):
            for i in range(len(chocolate_batch_produced.columns)):
                chocolate_batch_produced.iloc[-1, i] = math.ceil(chocolate_batch_produced.iloc[-1, i])
                break
        for x in range(len(chocolate_batch_produced.columns)):
            batch_quantity_temp = norm.rvs(loc = mean, scale = sd)
            chocolate_batch_produced.iloc[i, x] = math.ceil((chocolate.iloc[i, x] + chocolate_rollover.iloc[i, x]) / batch_quantity_temp)
            chocolate_rollover.iloc[i, x] = (chocolate_batch_produced.iloc[i,x] * batch_quantity_temp - chocolate.iloc[i,x])
            liquorice_produced.iloc[i].loc['Lakrids 1'] = liquorice_produced.iloc[i].loc['Lakrids 1'] + (chocolate_batch_produced.iloc[i, x] * batch_quantity_temp)
            batch_quantity_save.iloc[i,x] = batch_quantity_temp
    return liquorice_produced, chocolate_batch_produced, batch_quantity_save
