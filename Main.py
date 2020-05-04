# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020
@author: jakob
"""

from Demandgenerator import create_forecast_year
from Demandgenerator import distribute
from scipy.stats import norm
import simpy
       
    
    
def chocolate_batch_production(env, chocolate_machine, batch_time, batch_time_sd, batch_size, product_index, BOM):
    with chocolate_machine.request() as req:
        yield req
        batch_time = norm.rvs(loc = batch_time, scale = batch_time_sd)
    yield env.timeout(batch_time)   
    #print("batch of " + product_index + " finished at %d" % env.now )
    finished_product_container[product_index].put(norm.rvs(loc = batch_size, scale=batch_size_sd))

def start_week(env, week, forecast):
    batches_to_produce = forecast.loc[ : , forecast.columns.str.startswith("Lakrids") == False]
    batches_to_produce = batches_to_produce.iloc[week] / batch_size
    batches_not_evenly_distributed = batches_to_produce.copy()
    minutes_in_week_1shift = 5*8*60
    #if all batch times are 3 standard deviations above the mean we will use two shifts this week
    if batches_to_produce.sum() * (batch_time + 3*batch_time_sd) > minutes_in_week_1shift:
        shifts = 1
    else:
        shifts = 2
    for x in range(len(batches_to_produce)):
        batches_schedule[x] = batches_to_produce[x] // 5 #5 days in every week
        batches_not_evenly_distributed[x] = batches_to_produce[x] %  #remainder
    for j in range(len(batches_to_produce)):
        batches_to_produce[j] =    

def start_day(env, week, schedule):
    

def distribute(batches, days):
    base, extra = divmod(batches, days)
    return [base + (i < extra) for i in range(days)]

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


mean_demand_increase = 0.10
batch_size = 1875
batch_size_sd = batch_size*0.075

forecast2020 = create_forecast_year(2020, avg_demand_week0, mean_demand_increase, batch_size)


#in minutes
batch_time = 80
batch_time_sd = 0.1*80

number_of_machines = 8


env = simpy.Environment()
chocolate_machine = simpy.Resource(env, capacity=number_of_machines)

finished_product_container = BOM.fromkeys(BOM.keys())
for k in finished_product_container:
     finished_product_container[k] = simpy.Container(env)

env.process(start_week(env, 1, forecast2020))
