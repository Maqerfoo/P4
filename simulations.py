
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 17:02:43 2020
@author: jakob
"""

def unique_ingredients(BOM):
    list_of_ingredients = []
    for k,v in BOM.items():
        list_of_ingredients_temp = [t for t,c in BOM[k].items()]
        list_of_ingredients = list_of_ingredients + list_of_ingredients_temp
    list_of_ingredients = set(list_of_ingredients)
    ingredients_storage = dict.fromkeys(list_of_ingredients, 0)
    return ingredients_storage

def containers_full_levels(ingredients_container, BOM, forecast, percentage):
    for k,v in BOM.items():
        for t,c in BOM[k].items():
            last_week_quantity = forecast.iloc[-1]
            last_week_quantity = last_week_quantity.at[k]
            ingredients_container[t] = ingredients_container[t] + (c * last_week_quantity) * percentage
    return dict.copy(ingredients_container)