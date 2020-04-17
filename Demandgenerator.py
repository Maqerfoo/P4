# -*- coding: utf-8 -*-
"""
Takes args(year, projected average demand for first week of the year, mean increase, sd)
and outputs a stochastic yearly demand schedule. Every week is normally distributed 
over the mean values with sd of 10% of the mean. The demand increases stochastically
every week, by input mean(in percentage) and sd
"""
import numpy as np
import pandas as pd
import datetime
from scipy.stats import norm


def create_demand_week(avg_demand):
   ''' Create a weekly demand, normally distributed over an average, with sd = 1.10*mean'''
   demand_schedule = {}
   for k, v in avg_demand.items():
        demand_schedule[k] = norm.rvs(loc = v, scale = 0.1*v)
   return demand_schedule

def create_demand_year(year, avg_demand_base, mean, sd):
   ''' Create weekly demand for a full year, where the demand increases by  every week, normally distributed with sd=0.0025'''
    #finding weeks in a given year, and creating empty index-array
   weeks_in_year = datetime.date(year, 12, 28).isocalendar()[1]
   week_index = ["week0"]
   #creating an empty dataframe, for the weekly demands
   demand_year = pd.DataFrame(data = avg_demand_base, index=week_index)
   avg_demand = avg_demand_base.copy()
   for i in range(weeks_in_year):
       week_index = ["week" + str(i+1)]
       demand_schedule = create_demand_week(avg_demand)
       demand_week = pd.DataFrame(data = demand_schedule, index = week_index)
       
       demand_year = demand_year.append(demand_week) 
       #Incrementing the weekly demand, by a factor, normally distributed over input mean and sd
       for k,v in avg_demand.items():
           avg_demand[k] = v + (avg_demand_base[k] * norm.rvs(loc = mean, scale = sd))
   return demand_year        


avg_demand_week0 = {'Lakrids 1' : 4000, 'Lakrids 2' : 4000, 'Lakrids 3' : 4000,
          'Lakrids 4' : 4000, 'Chocolate A' : 7680, 'Chocolate B' : 7680, 
          'Chocolate C' : 7680, 'Chocolate D' : 7680, 'Chocolate E' : 7680,
          'Crispy Caramel' : 6400, 'Blackberry & Dark' : 6400, 
          'Twisted Banana' : 6400, 'Vanilla Mango' : 6400}   



demand2020 = create_demand_year(2020, avg_demand_week0, mean=0.15, sd=0.025)

