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
from sklearn.metrics import auc
from Plots import run_plots
import math
import simpy
import numpy as np
import pandas as pd
env = simpy.Environment()       



sales_price_pr_product = {'Salt' : 100, 'Sugar' : 8, 'Liquorice' : 400, 'Star anis' : 100,
                           'Fruit juice' : 100, 'Chocolate' : 120,'White chocolate' : 130,
                           'Liquorice coating' : 2750, 'Passionfruit coating' : 379,
                           'Coffee coating' : 139, 'Salt and caramel essence' : 122,
                           'Salmiak coating' : 179, 'Crisp' : 235, 'Blackberry essence' : 112.9,
                           'Banana coating' : 380, 'Vanilla essence' : 750, 'Mango coating' : 450}


avg_demand_week0 = {'Chocolate A' : 15360, 'Chocolate B' : 15360, 
          'Chocolate C' : 15360, 'Chocolate D' : 15360, 'Chocolate E' : 15360,
          'Crispy Caramel' : 12800, 'Blackberry & Dark' : 12800, 
          'Twisted Banana' : 12800, 'Vanilla Mango' : 12800}   

#all ingredients are in g, except for 'Lakrids 1', which is one piece.
BOM = {'Chocolate A' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Liquorice coating' : 0.7},
       'Chocolate B' : {'Sugar' : 4, 'Liquorice' : 1, 'White chocolate' : 4, 'Passionfruit coating' : 0.7}, 
       'Chocolate C' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Coffee coating' : 0.7}, 
       'Chocolate D' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Salt and caramel essence' : 0.5, 'Liquorice coating' : 0.7}, 
       'Chocolate E' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Salmiak coating' : 0.7},
       'Crispy Caramel' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Crisp' : 0.5, 'Liquorice coating' : 0.7}, 
       'Blackberry & Dark' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Blackberry essence' : 0.5, 'Liquorice coating' : 0.7},
       'Twisted Banana' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Banana coating' : 0.7},
       'Vanilla Mango' : {'Sugar' : 4, 'Liquorice' : 1, 'Chocolate' : 4, 'Vanilla essence' : 0.5, 'Mango coating' : 0.7}}



mean_demand_increase = 0.10
demand_sd = 0.05
batch_size = 1875
batch_size_sd = batch_size*0.075
holding_cost = 2.375
#in minutes
batch_time = 80
batch_time_sd = 0.1*80
number_of_machines = 8
reorder_threshold = 0.4
full_percentage = 1/5

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

###//// Visualization variables \\\\###


area_df = pd.DataFrame()
area_total_list = []
stock_outs_list = []
deliveries_list = []
stock_outs = 0
deliveries = 0


ingredients_levels = dict.fromkeys(ingredients_container_full)
for k,v in ingredients_levels.items():
    ingredients_levels[k] = {"level" : [ingredients_container_full[k]], "time" : [0]}   
    ingredients_level_total = {"level" : [0], "time" : [0]} 
               
            
#E-Kanban system code
def kanban_cycle(orders_pr_day_full_int):
    # To get the order_cycle we devide 5 (numbers of working days) with the EOQ (number of orders pr. week)
    lead_time_in_minutes = 12*60
    lead_time_from_supplier = lead_time_in_minutes/(24*60)
    b = math.ceil(orders_pr_day_full_int / 5)
    a = 1
    if b != 0:
        order_cycle = a / b
        c = lead_time_from_supplier/order_cycle
    else:
        c = 0
    return {'a' : a, 'b' : b, 'c' : c}


   
 # This is the modified EOQ formula that determines how much of a product to buy for each order while considering 
 # variables like: holding costs, order cost and the yearly/weekly demand
def EOQ(batches_to_produce, day, BOM, sales_price, shifts):  
    order_cost = 400
    #service level is static at 28% of the forecasted demand
    order_amount = unique_ingredients(BOM)
    EOQ_dict = dict.fromkeys(order_amount.keys(),0)
    #print(batches_to_produce)
    daily_forecast = dict.copy(batches_to_produce[int(day)])
    for k,v in daily_forecast.items():
        daily_forecast[k] = max(0,v * 1875)
        #print(daily_forecast[k])
    for k,v in BOM.items():
        for t,c in BOM[k].items():
            # We divide the forecast with one thousand because that will give us the order in kg which is assumed
            # to be a standard ordering of products
            #adding safety stock to order amount
            order_amount[t] = order_amount[t] + (c * daily_forecast[k])
            #print(str(k) + ", " + str(t) + ": " + str(order_amount[t]))
            EOQ_dict[t] = math.sqrt((2 * order_amount[t] * order_cost) / ((sales_price[t]*0.25)/360 ))
    #print(order_amount)
    orders_pr_day_full_int = dict.fromkeys(EOQ_dict.keys())
    for k,v in EOQ_dict.items():
        if EOQ_dict[k] != 0:
            orders_pr_day_full_int[k] = math.ceil( order_amount[k] / EOQ_dict[k] )
        else:
            orders_pr_day_full_int[k] = 0
    #print(orders_pr_day_full_int)
    return orders_pr_day_full_int



def iterate(env, iterations, ingredients_container_full):
    for i in range(iterations):
        global deliveries
        global stock_outs
        deliveries = 0
        stock_outs = 0
        global ingredients_container
        for k,v in ingredients_container.items():
            initial_value = ingredients_container_full[k]
            ingredients_container[k] = simpy.Container(env, init=initial_value)
        yield env.process(start_year(env, forecast2020, i))

def start_year(env, forecast, iteration):
    global ingredients_levels
    for k,v in ingredients_levels.items():
        ingredients_levels[k] = {"level" : [ingredients_container_full[k]], "time" : [env.now]}
    global ingredients_level_total
    ingredients_level_total = {"level" : [0], "time" : [env.now]} 
    for i in range(len(forecast)):
        #print("week" + str(i) + " started")
        week = env.process(start_week(env, i, forecast, ingredients_levels))
        yield week
    areas = dict.fromkeys(ingredients_levels.keys())
    area = auc([x - iteration * 534240 for x in ingredients_level_total["time"]] , ingredients_level_total["level"])
    #print(area)
    for k,v in ingredients_levels.items():
        areas[k] = auc([x - iteration * 534240 for x in ingredients_levels[k]["time"]], ingredients_levels[k]["level"])
    with open("reportoutput.txt", "a+") as f:    
        f.write("\n Simulation number: %d \n\n\n" %iteration)
        f.write("deliveries: %d \n" %deliveries)
        f.write("stock-outs: %d \n\n" %stock_outs)
        f.write("Inventory levels in kg*hours \n")
        f.write("total :" + str(area))
        for k,v in areas.items():
            f.write(str(k) + ": " + str(v) + "\n")
        f.close()
    global area_df
    areas_temp = pd.DataFrame(areas, index=[iteration])
    area_df = area_df.append(areas_temp)
    area_total_list.append(area)
    stock_outs_list.append(stock_outs)
    deliveries_list.append(deliveries)   

def start_week(env, week, forecast, ingredients_levels):
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
    days = int(5)
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
                    day1_to_5_batches[k+1][t] = max(0,day1_to_5_batches[k+1][t] - excess_batches)
                else:
                    weekly_rollover[t] = excess_batches
    #print("week ended at:" + str(env.now))
    

def start_day(env, day, schedule, shifts):
    print("day " + str(day) + " started at:" + str(env.now))
    #print(schedule)
    EOQ_dict = EOQ(schedule, day, BOM, sales_price_pr_product, shifts)
    kanban_cycles = dict.fromkeys(EOQ_dict.keys())
    number_of_deliveries = 0
    for k,v in kanban_cycles.items():
        kanban_cycles[k] = kanban_cycle(EOQ_dict[k])
        number_of_deliveries = max(number_of_deliveries, kanban_cycles[k]['b'])
    print("number of deliveries: " + str(number_of_deliveries))
    for i in range(number_of_deliveries):
        incoming_orders = [env.process(reorder(env, schedule[day], kanban_cycles, i, number_of_deliveries, shifts, BOM))]
    if number_of_deliveries != 0:
        yield incoming_orders[0]
    day_batches = []
    comparison_schedule = dict.fromkeys(schedule[day].keys(),0)
    while sum(schedule[day].values()) != sum(comparison_schedule.values()):
        for k,v in schedule[day].items():
            if comparison_schedule[k] != schedule[day][k]:
                comparison_schedule[k] = comparison_schedule[k] + 1
                #for i in range(int(schedule[day][k])):
                day_batches = [env.process(chocolate_batch_production(env, chocolate_machine, batch_time, batch_time_sd, k, BOM))]
    if len(day_batches) > 0:
        yield env.all_of(day_batches)
    temp_level = 0
    global ingredients_levels
    global ingredients_level_total
    for k,v in ingredients_levels.items():
        temp_level = temp_level + ingredients_container[k].level
    ingredients_level_total["level"].append(temp_level)
    ingredients_level_total["time"].append(env.now)
    week = env.now // (168*60)
    rest_of_day = 24 * 60 - (env.now - week * 168*60 - day * 24*60)
    if day == 4:
        yield env.timeout(rest_of_day + 2*24*60)
    else:
        yield env.timeout(rest_of_day)

    temp_level = 0
    for k,v in ingredients_levels.items():
        temp_level = temp_level + ingredients_container[k].level
    ingredients_level_total["level"].append(temp_level)
    ingredients_level_total["time"].append(env.now)
    #print("day " + str(day) + " ended at:" + str(env.now))
    #reorder here
    
def reorder(env, schedule, kanban_cycles, delivery_number, number_of_deliveries, shifts, BOM):
    global ingredients_levels
    global deliveries
    deliveries = deliveries + 1
    time_between_deliveries = (shifts*8*60)/number_of_deliveries
    #print("time until delivery:" + str(delivery_number*time_between_deliveries))
    service_level = 0.10
    yield env.timeout(delivery_number*time_between_deliveries)
    print("delivery here at time: " + str(env.now))
    current_levels = dict.fromkeys(ingredients_container.keys())
    to_order = dict.fromkeys(ingredients_container.keys(), 0)
    for k,v in current_levels.items():
        current_levels[k] = ingredients_container[k].level
    for k,v in BOM.items():
        for t,c in BOM[k].items():
            if kanban_cycles[t]['b'] != 0:
                service_stock = schedule[k] * 1875 * BOM[k][t] * service_level
                to_order[t] = to_order[t] + ((schedule[k] * 1875 * BOM[k][t] * kanban_cycles[t]["a"]*(kanban_cycles[t]['c']+1)/kanban_cycles[t]['b']) + service_stock)*1.10
            else:
                to_order[t] = 0
    for k,v in to_order.items():
        reorder_amount = max(0,to_order[k] - current_levels[k])
        if reorder_amount > 0:
            #print(str(reorder_amount) + "of" + str(k) + "delivered")
            ingredients_container[k].put(reorder_amount)
            ingredients_levels[k]["level"].append(ingredients_container[k].level)
            ingredients_levels[k]["time"].append(env.now)
                
            

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

def chocolate_batch_production(env, chocolate_machine, batch_time, batch_time_sd, product_index, BOM):
    with chocolate_machine.request() as req:
        yield req
        req2 = []
        global ingredients_levels
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
                print("inventory is at: " + str(ingredients_container[k].level) + " of " + str(k) )
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
            print("batch of " + product_index + " finished at %d" % env.now )
            finished_product_container[product_index].put(round(norm.rvs(loc = batch_size, scale=abs(batch_size_sd))))
        else:
            #print("batch of " + str(product_index) + " failed")
            yield env.timeout(0)


    

env.process(iterate(env, 100, ingredients_container_full))

env.run()    
    

stock_outs_sr = pd.Series(stock_outs_list, name="stock outs")
deliveries_sr = pd.Series(deliveries_list, name= "deliveries")
area_total_sr = pd.Series(area_total_list, name = "inventory level")
summary = area_total_sr.to_frame()
summary = summary.join(stock_outs_sr, how="left")
summary = summary.join(deliveries_sr, how="left")
with open("reportoutput.txt", "a+") as f:
    f.write("\n\n\n Mean values: \n")
    f.write(summary.mean().to_string() + "\n")
    f.write(area_df.mean().to_string() + "\n")
    f.close()   



summary.to_csv("summary.csv")
area_df.to_csv("all areas.csv")

