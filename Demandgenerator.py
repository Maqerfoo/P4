# -*- coding: utf-8 -*-
"""
Takes args(year, projected average demand for first week of the year, mean increase, sd)
and outputs a stochastic yearly demand schedule. Every week is normally distributed 
over the mean values with sd of 10% of the mean. The demand increases stochastically
every week, by input mean(in percentage) and sd
"""

import pandas as pd
import datetime
from scipy.stats import norm

def weeks_in_year_func(year):
    weeks = datetime.date(year, 12, 28).isocalendar()[1]
    return weeks

def create_demand_week(avg_demand, variation):
   ''' Create a weekly demand, normally distributed over an average, with sd = 1.10*mean'''
   demand_schedule = {}
   for k, v in avg_demand.items():
        demand_schedule[k] = round(norm.rvs(loc = v, scale = variation*v))
   return demand_schedule

def create_forecast_week(avg_demand):
   ''' round all entries in the week'''
   demand_schedule = {}
   for k, v in avg_demand.items():
        demand_schedule[k] = round(v)
   return demand_schedule

def create_demand_year(year, avg_demand_base, mean, sd, weekly_variation):
   ''' Create weekly demand for a full year, where the demand increases by  every week, normally distributed with sd=0.0025'''
    #finding weeks in a given year, and creating empty index-array
   weeks_in_year = weeks_in_year_func(year)
   week_index = []
   #creating an empty dataframe, for the weekly demands
   demand_year = pd.DataFrame(data = avg_demand_base, index=week_index)
   avg_demand = avg_demand_base.copy()
   for i in range(weeks_in_year):
       week_index = ["week" + str(i+1)]
       demand_schedule = create_demand_week(avg_demand, weekly_variation)
       demand_week = pd.DataFrame(data = demand_schedule, index = week_index)
       
       demand_year = demand_year.append(demand_week) 
       #Incrementing the weekly demand, by a factor, normally distributed over input mean and sd
       for k,v in avg_demand.items():
           avg_demand[k] = v + (avg_demand_base[k] * norm.rvs(loc = mean, scale = sd))
   forecast_year = create_forecast_year(weeks_in_year, avg_demand_base, mean)
   return demand_year, forecast_year        

def create_forecast_year(weeks_in_year, avg_demand_base, mean):
    ''' Create weekly demand for a full year, where the demand increases by  every week, normally distributed with sd=0.0025'''
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
    return forecast_year 