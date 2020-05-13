# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020
@author: jakob
"""

from Demandgenerator import create_forecast_year
from Demandgenerator import distribute_batches
from simulations import unique_ingredients
from scipy.stats import norm
import simpy
import numpy as np
import math
env = simpy.Environment()       
    
    
def chocolate_batch_production(env, chocolate_machine, batch_time, batch_time_sd, product_index, BOM):
    with chocolate_machine.request() as req:
        yield req
        batch_time = norm.rvs(loc = batch_time, scale = abs(batch_time_sd))
        yield env.timeout(batch_time)   
        print("batch of " + product_index + " finished at %d" % env.now )
        finished_product_container[product_index].put(round(norm.rvs(loc = batch_size, scale=abs(batch_size_sd))))

def start_day(env, day, schedule, shifts):
    print("day " + str(day) + " started at:" + str(env.now))
    print(schedule)
    for k,v in schedule[day].items():
        for i in range(int(schedule[day][k])):
            day_batches = [env.process(chocolate_batch_production(env, chocolate_machine, batch_time, batch_time_sd, k, BOM))]
    yield env.all_of(day_batches)
    yield env.timeout(20)
    print("day " + str(day) + " ended at:" + str(env.now))
    #change next days schedule here
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
        print("forecasted value is:" + str(forecast_val))
        demand = norm.rvs(loc = (forecast_val - safety_stock_in_sd*demand_sd*forecast_val) , scale = abs(demand_sd*forecast_val))
        print("demand is: " + str(demand))
        if max(0,demand) > 0:
            if demand < finished_product_container[k].level:
                print("demand taken: %d of " %demand + str(k))
                yield finished_product_container[k].get(round(demand))
            else: 
                demand = finished_product_container[k].level
                yield finished_product_container[k].get(round(demand))
                #report missed demand?
        else:
            yield env.timeout(0)


    
def start_week(env, week, forecast):
    print("week started at:" + str(env.now))
    batches_to_produce = forecast.loc[ : , forecast.columns.str.startswith("Lakrids") == False]
    batches_to_produce = batches_to_produce.iloc[week] / batch_size
    batches_to_produce = batches_to_produce.astype('int32')
    print(batches_to_produce)
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
            print("excess batches in storage: " + str(excess_batches) + "of " + str(t))
            if k > 0:
                if k != 4:       
                    day1_to_5_batches[k+1][t] = day1_to_5_batches[k+1][t] - excess_batches
                else:
                    weekly_rollover[t] = excess_batches
    print("week ended at:" + str(env.now))

def start_year(env, forecast):
    for i in range(len(forecast)):
        print("week" + str(i) + " started")
        week = env.process(start_week(env, i, forecast))
        yield week       

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
demand_sd = 0.05
batch_size = 1875
batch_size_sd = batch_size*0.075

forecast2020 = create_forecast_year(2020, avg_demand_week0, mean_demand_increase, batch_size)


#E-Kanban system code
def kanban_cycle(EOQ):
    # To get the order_cycle we devide 5 (numbers of working days) with the EOQ (number of orders pr. week)
    lead_time_in_hours = 14
    lead_time_from_supplier = lead_time_in_hours/24
    b = math.ceil(EOQ / 5)
    a = 1
    order_cycle = a / b
    c = lead_time_from_supplier/order_cycle
    return a, b, c

    

   
 # This is the modified EOQ formula that determines how much of a product to buy for each order while considering 
 # variables like: holding costs, order cost and the yearly/weekly demand
def EOQ(forecast, week):  
    holding_cost_pr_product = 2.375
    order_cost = 100
    order_amount = 0
    weekly_forecast = forecast.iloc[week]
    orders_pr_week = 0
    for k,v in BOM.items():
        for t,c in BOM[k].items():
            # We devide the forecast with one thousand because that will give us the order in tons which is assumed
            # to be a standard ordering of products
            order_amount = order_amount + ( (c * weekly_forecast.at[k]) /1000)
            units_pr_order = math.sqrt((2 * order_amount * order_cost)/(holding_cost_pr_product))
            orders_pr_week = order_amount / units_pr_order
            # We want the number of orders pr. week in full integers because you cannot make 6.2563 orders
            orders_pr_week_full_int = math.ceil(orders_pr_week)
    print(order_amount)
    print(orders_pr_week_full_int)
    return orders_pr_week_full_int

def kanban_number(forecast, week, safety_stock):
    total_demand = 0 
    bin_size = 5
    safety_kanban_number = safety_stock
    weekly_forecast = forecast.iloc[week]
    for k,v in BOM.items():
        for t,c in BOM[k].items():
            total_demand = total_demand + ( (c * weekly_forecast.at[k]) /1000)
            kanban_number = (((total_demand * a (c + 1)/b + safety_kanban_number) / bin_size)
    return kanban_number


def safety_kanban_number(EOQ, week, forecast, ):
    service_level = 1.28
    standard_deviation_leadtime =
    damand_average = 0
    
    forecastweek = batches.to_dict()
    for k,v in forecastweek.items():
        #we forecast 3 standard deviations over the mean demand
        forecast_val = v / 5
        #safety-stock is being accounted for here. Essentially the scheduled production is set to be 3
        #standard deviations above the mean of the demand
        safety_stock_in_sd = 3
        #possibility here for dynamic safety-stock!!!
        print("forecasted value is:" + str(forecast_val))
        demand = norm.rvs(loc = (forecast_val - safety_stock_in_sd*demand_sd*forecast_val) , scale = abs(demand_sd*forecast_val))
        print("demand is: " + str(demand))
       

#in minutes
batch_time = 80
batch_time_sd = 0.1*80

number_of_machines = 8

chocolate_machine = simpy.Resource(env, capacity=number_of_machines)

finished_product_container = dict.fromkeys(BOM.keys())
for k in finished_product_container:
     finished_product_container[k] = simpy.Container(env, init=2000)

ingredients_container = unique_ingredients(BOM)
for k,v in ingredients_container.items():
    ingredients_container[k] = simpy.Container(env, init=10000)

weekly_rollover = dict.fromkeys(BOM.keys(),0)
env.process(start_year(env, forecast2020))
#env.run()
