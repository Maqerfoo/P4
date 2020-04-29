# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020
@author: jakob
"""

from Demandgenerator import create_demand_year
from Demandgenerator import create_forecast_year
from productionscheduler import batches_produced
from productionscheduler import batches_produced_no_variance
from productionscheduler import weekly_materials
from productionscheduler import liquorice_from_chocolate
import simpy
from scipy.stats import norm


def chocolate_batch_production(env, batch_time, chocolate_machine):
    with chocolate_machine.request() as req:
        yield req
    batch_time = norm.rvs(loc = batch_time, scale = 0.1*batch_time)
    yield env.timeout(batch_time)


avg_demand_week0 = {'Lakrids 1' : 8000.0, 'Lakrids 2' : 8000.0, 'Lakrids 3' : 8000,
          'Lakrids 4' : 8000, 'Chocolate A' : 15360, 'Chocolate B' : 15360, 
          'Chocolate C' : 15360, 'Chocolate D' : 15360, 'Chocolate E' : 15360,
          'Crispy Caramel' : 12800, 'Blackberry & Dark' : 12800, 
          'Twisted Banana' : 12800, 'Vanilla Mango' : 12800}   

#all ingredients are in g, except for 'Lakrids 1', which is one piece.
BOM = {'Lakrids 1' : {'Salt' : 0.12, 'Sugar' : 2, 'Raw liquorice' : 0.45, 'Star anise' : 0.05}, 
       'Lakrids 2' : {'Salt' : 0.17, 'Sugar' : 2, 'Raw liquorice' : 0.45}, 
       'Lakrids 3' : {'Salt' : 0.12, 'Sugar' : 2, 'Raw liquorice' : 0.45, 'Fruit juice' : 0.05},
       'Lakrids 4' : {'Salt' : 0.12, 'Sugar' : 2, 'Raw liquorice' : 0.45, 'Habanero' : 0.05},
       'Chocolate A' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Liquorice coating' : 0.02},
       'Chocolate B' : {'Sugar' : 4, 'Lakrids 1' : 1, 'White Chocolate' : 4, 'Passionfruit coating' : 0.02}, 
       'Chocolate C' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Coffee coating' : 0.02}, 
       'Chocolate D' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Salt and caramel essence' : 0.04, 'liquorice coating' : 0.02}, 
       'Chocolate E' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Salmiak coating' : 0.02},
       'Crispy Caramel' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Crisp' : 0.04, 'liquorice coating' : 0.02}, 
       'Blackberry & Dark' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Blackberry essence' : 0.02, 'liquorice coating' : 0.02},
       'Twisted Banana' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Banana coating' : 0.02},
       'Vanilla Mango' : {'Sugar' : 4, 'Lakrids 1' : 1, 'Chocolate' : 4, 'Vanilla essence' : 0.02, 'Mango coating' : 0.02}}

demand2020 = create_demand_year(2020, avg_demand_week0, mean=0.10, sd=0.025)
forecast2020 = create_forecast_year(2020, avg_demand_week0, mean=0.10)

#adjusting for fixed batch quantity normally distributed over mean with sd
#also adjusting for rollover-effects of over-production, due to only being able to produce full batches
chocolate_batch_production_demand, batch_quantity_demand = batches_produced(demand2020, mean = 1875, sd = 1875*0.05)
#adding the liquorices needed for the chocolates
liquorice_demand = liquorice_from_chocolate(demand2020, chocolate_batch_production_demand, batch_quantity_demand)
#merging everything in one dataframe
yearly_usage = liquorice_demand.merge(chocolate_batch_production_demand.multiply(batch_quantity_demand).round(), how='inner', left_index=True, right_index=True)


chocolate_batch_production_forecast, batch_quantity_forecast = batches_produced(forecast2020, mean = 1875, sd=0)
liquorice_forecast = liquorice_from_chocolate(forecast2020, chocolate_batch_production_forecast, batch_quantity_forecast)
yearly_forecast = liquorice_forecast.merge(chocolate_batch_production_forecast.multiply(1875.0), how='inner', left_index=True, right_index=True)
for i in range(len(yearly_forecast)):
    temp_sum = sum(chocolate_batch_production_forecast.iloc[i]) * 1875.0
    yearly_forecast.iat[i,0] += temp_sum
    


week2_usage = weekly_materials(BOM, yearly_usage, 1)

env = simpy.Environment()
chocolate_machine = simpy.Resource(env, capacity=8)

for i in range(len(chocolate_batch_production_demand)):
    week_usage = weekly_materials(BOM, yearly_usage, i)
    for x in range(len(chocolate_batch_production_demand.columns)):
        env.process



