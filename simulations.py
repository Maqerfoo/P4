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
    ingredients_storage = dict.fromkeys(list_of_ingredients)
    return ingredients_storage
