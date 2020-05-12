# -*- coding: utf-8 -*-
"""
Takes args(year, projected average demand for first week of the year, mean increase, sd)
and outputs a stochastic yearly demand schedule. Every week is normally distributed 
over the mean values with sd of 10% of the mean. The demand increases stochastically
every week, by input mean(in percentage) and sd
"""

import pandas as pd
import numpy as np
import datetime
from scipy.stats import norm
import math


def distribute_batches(batches, days, day_total):
    base = batches // days
    extra = batches % days
    day1_to_5 = np.zeros(days, dtype=int)
    day1_to_5.fill(base)
    for i in range(int(extra)):
        idx = np.argmin(day_total)
        day1_to_5[idx] = day1_to_5[idx] + 1
        day_total[idx] = day_total[idx] + 1
    return day1_to_5

def weeks_in_year_func(year):
    weeks = datetime.date(year, 12, 28).isocalendar()[1]
    return weeks

def create_demand_week(forecast_week, variation):
   ''' Create a weekly demand, normally distributed over an average, with sd = variation*mean'''
   demand_schedule = {}
   for k, v in forecast_week.items():
        demand_schedule[k] = round(norm.rvs(loc = v, scale = abs(variation*v)))
   return demand_schedule

def create_forecast_week(avg_demand):
   ''' round all entries in the week'''
   demand_schedule = {}
   for k, v in avg_demand.items():
        demand_schedule[k] = round(v)
   return demand_schedule

#we can only produce integer number of batches of quantity 1875. So we produce
#lowest integer, greater than batch quantity. Then we need to adjust for rollover
#from previous weeks production


def batches_produced(forecast_year, batch_size):
    chocolate = forecast_year.loc[ : , forecast_year.columns.str.startswith("Lakrids") == False]
    chocolate_rollover = chocolate.copy()
    for col in chocolate_rollover.columns:
        chocolate_rollover[col].values[:] = 0
    #the chocolate output from one individual batch is stochastic - the mean of all batches is 1875
    chocolate_batch_produced = chocolate_rollover.copy()
    for i in range(len(chocolate_batch_produced)):
        for x in range(len(chocolate_batch_produced.columns)):
            chocolate_batch_produced.iat[i, x] = math.ceil((chocolate.iat[i, x] + chocolate_rollover.iat[i, x]) / batch_size)
            chocolate_rollover.iat[i, x] = (chocolate_batch_produced.iat[i,x] * batch_size - chocolate.iat[i,x])
    return chocolate_batch_produced.multiply(batch_size)

def create_forecast_year(year, avg_demand_base, mean, batch_size):
    ''' Create weekly demand for a full year, where the demand increases by  every week, normally distributed with sd=0.0025'''
    weeks_in_year = weeks_in_year_func(year)
    #creating an empty dataframe, for the weekly demands
    week_index = []
    forecast_year = pd.DataFrame(data = avg_demand_base, index=week_index)
    avg_demand = avg_demand_base.copy()
    for i in range(weeks_in_year):
        week_index = ["week" + str(i+1)]
        forecast_schedule = create_forecast_week(avg_demand)
        forecast_week = pd.DataFrame(data = forecast_schedule, index = week_index)     
        forecast_year = forecast_year.append(forecast_week) 
        #Incrementing the weekly demand, by a factor, normally distributed over input mean and sd
        for k,v in avg_demand.items():
            avg_demand[k] = v + (avg_demand_base[k] * mean)
    forecast_year = batches_produced(forecast_year, batch_size)
    return forecast_year 

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
