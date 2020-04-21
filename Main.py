# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:21:10 2020
@author: jakob
"""

from Demandgenerator import create_demand_year
from productionscheduler import batches_produced



avg_demand_week0 = {'Lakrids 1' : 8000, 'Lakrids 2' : 8000, 'Lakrids 3' : 8000,
          'Lakrids 4' : 8000, 'Chocolate A' : 15360, 'Chocolate B' : 15360, 
          'Chocolate C' : 15360, 'Chocolate D' : 15360, 'Chocolate E' : 15360,
          'Crispy Caramel' : 12800, 'Blackberry & Dark' : 12800, 
          'Twisted Banana' : 12800, 'Vanilla Mango' : 12800}   

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

demand2020 = create_demand_year(2020, avg_demand_week0, mean=0.10, sd=0.025)


chocolate_batch_production, liquorice_production = batches_produced(demand2020, mean = 1875, sd = 1875*0.05)
