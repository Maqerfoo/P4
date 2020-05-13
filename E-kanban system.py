# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 19:46:57 2020

@author: robot
"""
import math

# holding_cost_pr_product_BOM is the cost of the products 
holding_cost_pr_product = {'Salt' : 100, 'Sugar' : 100, 'Raw liquorice' : 100, 'Star anis' : 100,
                           'Fruit juice' : 100, 'Habanero' : 100, 'Chocolate' : 100, 
                           'White chocolate' : 100, 'Liquorice coating' : 100, 'Passionfruit coating' : 100,
                           'Coffee coating' : 100, 'Salt and caramel essence' : 100,
                           'Salmiak coating' : 100, 'Crisp' : 100, 'Blackberry essence' : 100,
                           'Banana coating' : 100, 'Vanilla essence' : 100, 'Mango coating' : 100}
#E-Kanban system code
def kanban_cycle_week_product_x(weekly_product_demand, yearly_usage, modifyed_EOQ, lead_time_BOM, deliveries_a_day):
    
    
    # we use all the values from the different products in the different weeks in yearly_usage to determine the
    # of a certain product and use that to determine the kanban cycle.
    for i in (yearly_usage):
       weekly_product_demand = yearly_usage.iloc[i].loc
   
 # This is the modified EOQ formula that determines how much of a product to buy for each order while considering 
 # variables like: holding costs, order cost and the yearly/weekly demand
def modifyed_EOQ(holding_cost_pr_product, order_cost, yearly_forecast, weekly_usage_in_orders):  
    for i in range(len(yearly_forecast)):
        for x in range(len(yearly_forecast.columns)):
            for j in BOM.keys():
                weekly_usage_in_orders = BOM.keys[j] * yearly_forecast[i, x] 
            EOQ = sqrt((2*yearly_forecast.iat[i, x] * order_cost.at)/(holding_cost_pr_product))
    return EOQ
    
#((ingredienser_af_lakrids1 * amount_of_lakrids1) * order_cost_lakrids1) / holding_cost_lakrids1
    

#E-Kanban system code
def kanban_cycle_week_product_x(weekly_product_demand, yearly_usage, modifyed_EOQ, lead_time_BOM, deliveries_a_day):
    lead_time_from_supplier = 12
    # To get the order_cycle we devide 5 (numbers of working days) with the EOQ (number of orders pr. week)
    if (EOQ() % 5) == 0:
        order_cycle = a / b
        b = EOQ() / 5
        a = 1
        c = lead_time_from_supplier/order_cycle
    else:
        order_cycle = a /b
        b = EOQ() // 5) 
    order_cycle = 5 / EOQ()
    
    # we use all the values from the different products in the different weeks in yearly_usage to determine the
    # of a certain product and use that to determine the kanban cycle.
    for i in (yearly_usage):
       weekly_product_demand = yearly_usage.iloc[i].loc
   
 # This is the modified EOQ formula that determines how much of a product to buy for each order while considering 
 # variables like: holding costs, order cost and the yearly/weekly demand
def EOQ(holding_cost_pr_product, order_cost, weekly_usage_in_rawmaterials):  
    #for i in range(len(yearly_forecast)):
        #for x in range(len(yearly_forecast.columns)):
    holding_cost_pr_product = 0.5
    oder_cost = 50 
    for j in BOM.keys():
        for i in unique_ingredients:
            list_of_used_rawmaterials = BOM.keys[] * unique_ingredients()
            # We need the weekly usage in kg so we devide with 1000.
            weekly_usage_in_rawmaterials = dict.fromkeys(list_of_used_rawmaterials) / 1000
            orders_pr_week = math.sqrt((2*weekly_usage_in_rawmaterials[i, x] * order_cost)/(holding_cost_pr_product))
    return orders_pr_week
    
#((ingredienser_af_lakrids1 * amount_of_lakrids1) * order_cost_lakrids1) / holding_cost_lakrids1

