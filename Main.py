# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020
@author: jakob
"""

from Demandgenerator import create_demand_year
from productionscheduler import weekly_materials_usage
from productionscheduler import yearly_usage_function
import simpy
from scipy.stats import norm



def chocolate_batch_production(env, batch_time, chocolate_machine, product_index):
    with chocolate_machine.request() as req:
        yield req
        batch_time = norm.rvs(loc = batch_time, scale = 0.1*batch_time)
        yield env.timeout(batch_time)
        print("batch of " + product_index + " finished at %d" % env.now )


avg_demand_week0 = {'Lakrids 1' : 8000, 'Lakrids 2' : 8000, 'Lakrids 3' : 8000,
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


#the increase in demand, for every week is normally distributed over mean=mean_demand_increase with sd=mean_demand_increase_sd
mean_demand_increase = 0.10
mean_demand_increase_sd = 0.025
#the demand of every product is stochastic. Normally distributed with sd=weekly_variation, over the increasing demand values
product_variation = 0.10


demand2020, forecast2020 = create_demand_year(2020, avg_demand_week0, mean_demand_increase, mean_demand_increase_sd, product_variation)

#setting the mean chocolate batch size, normally distributed with sd = batch_size_variation
batch_size = 1875
batch_size_variation = 0.05*batch_size

yearly_usage, batch_size_actual, batches_demand = yearly_usage_function(demand2020, mean = batch_size, sd = batch_size_variation)
yearly_forecast, batch_size_forecast, batches_forecast = yearly_usage_function(forecast2020, mean = batch_size, sd=0)
    
week1_usage = weekly_materials_usage(BOM, yearly_usage, 0)
week1_forecast = weekly_materials_usage(BOM, yearly_forecast, 0)

#in minutes
batch_time = 80

env = simpy.Environment()
chocolate_machine = simpy.Resource(env, capacity=8)

for i in range(len(batches_demand)):
    print("week" + str(i))
    for x in range(len(batches_demand.iloc[i])):
        for j in range(int(batches_demand.iat[i,x])):
            env.process(chocolate_batch_production(env, batch_time, chocolate_machine, batches_demand.columns[x]))

env.run()   








