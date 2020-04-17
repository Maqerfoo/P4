# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020

@author: jakob
"""

from Demandgenerator import create_demand_year


avg_demand_week0 = {'Lakrids 1' : 4000, 'Lakrids 2' : 4000, 'Lakrids 3' : 4000,
          'Lakrids 4' : 4000, 'Chocolate A' : 7680, 'Chocolate B' : 7680, 
          'Chocolate C' : 7680, 'Chocolate D' : 7680, 'Chocolate E' : 7680,
          'Crispy Caramel' : 6400, 'Blackberry & Dark' : 6400, 
          'Twisted Banana' : 6400, 'Vanilla Mango' : 6400}   


demand2020 = create_demand_year(2020, avg_demand_week0, mean=0.15, sd=0.025)