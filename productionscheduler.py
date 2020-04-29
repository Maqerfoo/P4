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
    chocolate_rollover = chocolate.copy()
    for col in chocolate_rollover.columns:
        chocolate_rollover[col].values[:] = 0
    #the chocolate output from one individual batch is stochastic - the mean of all batches is 1875
    chocolate_batch_produced = chocolate_rollover.copy()
    batch_quantity_save = chocolate_rollover.copy()
    for i in range(len(chocolate_batch_produced)):
        for x in range(len(chocolate_batch_produced.columns)):
            batch_quantity_temp = norm.rvs(loc = mean, scale = sd)
            chocolate_batch_produced.iat[i, x] = math.ceil((chocolate.iat[i, x] + chocolate_rollover.iat[i, x]) / batch_quantity_temp)
            chocolate_rollover.iat[i, x] = (chocolate_batch_produced.iat[i,x] * batch_quantity_temp - chocolate.iat[i,x])
            batch_quantity_save.iat[i,x] = batch_quantity_temp
            #print(liquorice_produced)
    return chocolate_batch_produced, batch_quantity_save

def batches_produced_no_variance(demand, mean):
    chocolate = demand.loc[ : , demand.columns.str.startswith("Lakrids") == False]
    chocolate_rollover = chocolate.copy()
    for col in chocolate_rollover.columns:
        chocolate_rollover[col].values[:] = 0
    #the chocolate output from one individual batch is stochastic - the mean of all batches is 1875
    chocolate_batch_produced = chocolate_rollover.copy()
    for i in range(len(chocolate_batch_produced)):
        for x in range(len(chocolate_batch_produced.columns)):
            batch_quantity_temp = mean
            chocolate_batch_produced.iat[i, x] = math.ceil((chocolate.iat[i, x] + chocolate_rollover.iat[i, x]) / batch_quantity_temp)
            chocolate_rollover.iat[i, x] = (chocolate_batch_produced.iat[i,x] * batch_quantity_temp - chocolate.iat[i,x])
            #print(liquorice_produced)
    return chocolate_batch_produced

def liquorice_from_chocolate(demand, chocolate_batch_production, chocolate_batch_quantity):
    liquorice_production = demand.loc[ : , demand.columns.str.startswith("Lakrids")]
    for i in range(len(demand)):
        for x in range(len(chocolate_batch_production.columns)):
            liquorice_production.iloc[i].at['Lakrids 1'] = liquorice_production.iloc[i].at['Lakrids 1'] + (chocolate_batch_production.iat[i, x] * chocolate_batch_quantity.iat[i,x])
    return liquorice_production


def weekly_materials(BOM, production_schedule, week_index):
    week = BOM.copy()
    for k,v in BOM.items():
          to_produce = round(production_schedule.iloc[week_index].loc[k])
          materials = BOM[k].copy()
          for t,c in BOM[k].items():
             materials[t] = c * to_produce
          week[k] = materials 
    return week