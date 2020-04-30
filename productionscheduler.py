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


def liquorice_from_chocolate(demand, chocolate_batch_production, chocolate_batch_size):
    liquorice_production = demand.loc[ : , demand.columns.str.startswith("Lakrids")]
    for i in range(len(demand)):
        j = liquorice_production.iloc[i].index.get_loc('Lakrids 1')
        for x in range(len(chocolate_batch_production.columns)):
            liquorice_production.iloc[i , j] +=  (chocolate_batch_production.iat[i, x] * chocolate_batch_size.iat[i,x])
    return liquorice_production


def weekly_materials_usage(BOM, yearly_usage, week_index):
    week = BOM.copy()
    for k,v in BOM.items():
        j = yearly_usage.iloc[week_index].index.get_loc(k)
        to_produce = round(yearly_usage.iat[week_index, j])
        materials = BOM[k].copy()
        for t,c in BOM[k].items():
            materials[t] = c * to_produce
        week[k] = materials 
    return week

def yearly_usage_function(demand, mean, sd):
    chocolate, batch_size = batches_produced(demand, mean, sd)
    liquorice = liquorice_from_chocolate(demand, chocolate, batch_size)
    yearly_usage = liquorice.merge(chocolate.multiply(batch_size).round(), how='inner', left_index=True, right_index=True)
    return yearly_usage, batch_size, chocolate