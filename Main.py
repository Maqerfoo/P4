# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020
@author: jakob
"""

from Demandgenerator import create_forecast_year
from Demandgenerator import distribute_batches
from simulations import unique_ingredients
from simulations import containers_full_levels
from scipy.stats import norm
import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
env = simpy.Environment()       
    
    
def chocolate_batch_production(env, chocolate_machine, batch_time, batch_time_sd, product_index, BOM):
    with chocolate_machine.request() as req:
        yield req
        req2 = []
        temp_levels = dict.copy(dict.fromkeys(ingredients_levels.keys()))
        for k,v in temp_levels.items():
            temp_levels[k] = {"level" : None, "time" : None}
        req_trig = True
        for k,v in BOM[product_index].items():
            if ingredients_container[k].level > (v * batch_size):
                req2.append(ingredients_container[k].get(v * batch_size))
                temp_levels[k]["level"] = ingredients_container[k].level
                temp_levels[k]["time"] = env.now
            else: 
                print("experienced stock-out at " + str(env.now) + "of product: " + str(k) )
                print("inventory is at: " + str(ingredients_container[k].level) )
                global stock_outs
                stock_outs = stock_outs + 1
                req_trig = False
        if req_trig == True: 
            yield env.all_of(req2)
            for k,v in temp_levels.items():
                if temp_levels[k]["level"] is not None:
                    ingredients_levels[k]["level"].append(temp_levels[k]["level"])
                    ingredients_levels[k]["time"].append(temp_levels[k]["time"])
            batch_time = norm.rvs(loc = batch_time, scale = abs(batch_time_sd))
            yield env.timeout(batch_time)   
            #print("batch of " + product_index + " finished at %d" % env.now )
            finished_product_container[product_index].put(round(norm.rvs(loc = batch_size, scale=abs(batch_size_sd))))
        else:
            #print("batch of " + str(product_index) + " failed")
            yield env.timeout(0)

def reorder():
    for k,v in ingredients_container.items():
        if ingredients_container[k].level < ingredients_container_full[k] * reorder_threshold:
            global deliveries
            deliveries = deliveries + 1
            for k,v in ingredients_container.items():
                print("level of %s is:" %k + str(ingredients_container[k].level))
                print("reordered :" + str(ingredients_container_full[k] - ingredients_container[k].level))
                reorder_amount = ingredients_container_full[k] - ingredients_container[k].level
                if max(0,reorder_amount) != 0:
                    ingredients_container[k].put(ingredients_container_full[k] - ingredients_container[k].level)
                    ingredients_levels[k]["level"].append(ingredients_container[k].level)
                    ingredients_levels[k]["time"].append(env.now)
                
            
    

def start_day(env, day, schedule, shifts):
    print("day " + str(day) + " started at:" + str(env.now))
    for k,v in schedule[day].items():
        for i in range(int(schedule[day][k])):
            day_batches = [env.process(chocolate_batch_production(env, chocolate_machine, batch_time, batch_time_sd, k, BOM))]
    yield env.all_of(day_batches)
    temp_level = 0
    for k,v in ingredients_levels.items():
        temp_level = temp_level + ingredients_container[k].level
    ingredients_level_total["level"].append(temp_level)
    ingredients_level_total["time"].append(env.now)
    reorder()
    temp_level = 0
    for k,v in ingredients_levels.items():
        temp_level = temp_level + ingredients_container[k].level
    ingredients_level_total["level"].append(temp_level)
    ingredients_level_total["time"].append(env.now)
    yield env.timeout(20)
    print("day " + str(day) + " ended at:" + str(env.now))
    #reorder here


def demand_day(env, week, batches):
    batches = batches * batch_size
    forecastweek = batches.to_dict()
    for k,v in forecastweek.items():
        #we forecast 3 standard deviations over the mean demand
        forecast_val = v / 5
        #safety-stock is being accounted for here. Essentially the scheduled production is set to be 3
        #standard deviations above the mean of the demand
        safety_stock_in_sd = 3
        #possibility here for dynamic safety-stock!!!
        demand = norm.rvs(loc = (forecast_val - safety_stock_in_sd*demand_sd*forecast_val) , scale = abs(demand_sd*forecast_val))
        if max(0,demand) > 0:
            if demand < finished_product_container[k].level:
                #print("demand taken: %d of " %demand + str(k))
                yield finished_product_container[k].get(round(demand))
            else: 
                #report missed demand?
                demand = finished_product_container[k].level
                #print("demand is: " + str(demand))
                if demand != 0:
                    yield finished_product_container[k].get(round(demand))
                else: 
                    yield env.timeout(0)
        else:
            yield env.timeout(0)


    
def start_week(env, week, forecast):
    print("week %d started at:" %week + str(env.now))
    batches_to_produce = forecast.loc[ : , forecast.columns.str.startswith("Lakrids") == False]
    batches_to_produce = batches_to_produce.iloc[week] / batch_size
    batches_to_produce = batches_to_produce.astype('int32')
    minutes_in_week_1shift = 5*8*60
    #if all batch times are 3 standard deviations above the mean we will use two shifts this week
    if batches_to_produce.sum() * (batch_time + 3*batch_time_sd) > minutes_in_week_1shift:
        shifts = 1
    else:
        shifts = 2
    days = 5
    day1_to_5_batches = [0] * days
    batches_temp = batches_to_produce.copy()
    batches_temp.values[:] = 0
    for i in range(days):
        day1_to_5_batches[i] = batches_temp.to_dict()
    day1_to_5_batches_total = np.zeros(days, dtype=int)
    for x in range(len(batches_to_produce)):
         day1_to_5_batches_temp = np.zeros(days, dtype=int)
         idx = batches_to_produce.index[x]
         day1_to_5_batches_temp = distribute_batches(int(batches_to_produce[x]), days, day1_to_5_batches_total)
         for j in range(days):
             day1_to_5_batches[j][idx] = day1_to_5_batches_temp[j]
             if j == 0:
                 day1_to_5_batches[j][idx] = day1_to_5_batches[j][idx] + weekly_rollover[idx]
    for k in range(days):
        day_process = env.process(start_day(env, k, day1_to_5_batches, shifts))
        yield day_process
        demand_proc = env.process(demand_day(env, week , batches_to_produce))
        yield demand_proc
        #here we update the schedule continously, accounting for the chocolates already in storage!!
        for t,c in day1_to_5_batches[k].items():
            excess_batches = max(0,int(finished_product_container[t].level // batch_size))
            #print("excess batches in storage: " + str(excess_batches) + "of " + str(t))
            if k > 0:
                if k != 4:       
                    day1_to_5_batches[k+1][t] = day1_to_5_batches[k+1][t] - excess_batches
                else:
                    weekly_rollover[t] = excess_batches
    #print("week ended at:" + str(env.now))

def start_year(env, forecast):
    for i in range(len(forecast)):
        #print("week" + str(i) + " started")
        week = env.process(start_week(env, i, forecast))
        yield week       

avg_demand_week0 = {'Chocolate A' : 15360, 'Chocolate B' : 15360, 
          'Chocolate C' : 15360, 'Chocolate D' : 15360, 'Chocolate E' : 15360,
          'Crispy Caramel' : 12800, 'Blackberry & Dark' : 12800, 
          'Twisted Banana' : 12800, 'Vanilla Mango' : 12800}   

#all ingredients are in g, except for 'Lakrids 1', which is one piece.
BOM = {'Chocolate A' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Liquorice coating' : 0.02},
       'Chocolate B' : {'Sugar' : 4, 'Liquorice' : 1, 'White Chocolate' : 4, 'Passionfruit coating' : 0.02}, 
       'Chocolate C' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Coffee coating' : 0.02}, 
       'Chocolate D' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Salt and caramel essence' : 0.04, 'liquorice coating' : 0.02}, 
       'Chocolate E' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Salmiak coating' : 0.02},
       'Crispy Caramel' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Crisp' : 0.04, 'liquorice coating' : 0.02}, 
       'Blackberry & Dark' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Blackberry essence' : 0.02, 'liquorice coating' : 0.02},
       'Twisted Banana' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Banana coating' : 0.02},
       'Vanilla Mango' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Vanilla essence' : 0.02, 'Mango coating' : 0.02}}


mean_demand_increase = 0.10
demand_sd = 0.05
batch_size = 1875
batch_size_sd = batch_size*0.075
#in minutes
batch_time = 80
batch_time_sd = 0.1*80
number_of_machines = 8
reorder_threshold = 0.4
full_percentage = 2/5


forecast2020 = create_forecast_year(2020, avg_demand_week0, mean_demand_increase, batch_size)


chocolate_machine = simpy.Resource(env, capacity=number_of_machines)

finished_product_container = dict.fromkeys(BOM.keys())
for k in finished_product_container:
     finished_product_container[k] = simpy.Container(env, init=0)


ingredients_container = unique_ingredients(BOM)

#we choose the full level of the containers to be the necessary ingredients for the forecasted values of 
#the last weeks production. We multiply by full_percentage, to get one days production.
ingredients_container_full = containers_full_levels(ingredients_container, BOM, forecast2020, full_percentage)
        

for k,v in ingredients_container.items():
    initial_value = ingredients_container_full[k]
    ingredients_container[k] = simpy.Container(env, init=initial_value)

weekly_rollover = dict.fromkeys(BOM.keys(),0)
env.process(start_year(env, forecast2020))

###//// Visualization variables \\\\###
ingredients_levels = dict.fromkeys(ingredients_container_full)
for k,v in ingredients_levels.items():
    ingredients_levels[k] = {"level" : [ingredients_container_full[k]], "time" : [0]}

ingredients_level_total = {"level" : [0], "time" : [0]}

stock_outs = 0
deliveries = 0  
  
env.run()

inventory_levels_dataframes = dict.copy(dict.fromkeys(ingredients_levels.keys() ))
inventory_level_total_df = pd.DataFrame(ingredients_level_total, columns = dict.fromkeys(ingredients_level_total.keys() ))
for k,v in ingredients_levels.items():
    inventory_levels_dataframes[k] = pd.DataFrame(ingredients_levels[k], columns = dict.fromkeys(ingredients_levels[k].keys() ))

inventory_level_df_short = inventory_level_total_df[0:100]
inventory_level_df_short.plot(kind = "line", x = "time", y = "level")
