# -*- coding: utf-8 -*-
"""
Created on Mon May 18 10:37:58 2020

@author: jakob
"""
import pandas as pd
import matplotlib.pyplot as plt

def run_plots(ingredients_level_total, ingredients_levels):
    inventory_levels_dataframes = dict.copy(dict.fromkeys(ingredients_levels.keys() ))
    inventory_level_total_df = pd.DataFrame(ingredients_level_total, columns = dict.fromkeys(ingredients_level_total.keys() ))
    inventory_level_total_df["level"] = inventory_level_total_df["level"] / 1000
    inventory_level_total_df["time"] = inventory_level_total_df["time"] / 60
    
    for k,v in ingredients_levels.items():
        inventory_levels_dataframes[k] = pd.DataFrame(ingredients_levels[k], columns = dict.fromkeys(ingredients_levels[k].keys() ))
        inventory_levels_dataframes[k]["level"] = inventory_levels_dataframes[k]["level"] / 1000
        inventory_levels_dataframes[k]["time"] = inventory_levels_dataframes[k]["time"] / 60
    
    inventory_level_total_df.plot(kind = "line", x = "time", y = "level",)
    mean = round(inventory_level_total_df["level"].mean(), 2)
    [ymin, ymax] = plt.gca().get_ylim()
    ax = plt.gca()
    ax.text(0, ymax - ymax*0.1, 'mean levels = ' + str(mean) + " kg", style='italic',
            bbox={'facecolor': 'red', 'alpha': 0.6, 'pad': 10},
            verticalalignment='top', horizontalalignment='left',)
    ax.set_xlabel("time in hours")
    ax.set_ylabel("inventory levels in kg")
    
    for k,v in inventory_levels_dataframes.items():
        inventory_levels_dataframes[k].plot(kind = "line", x= "time", y= "level", label = str(k)).set_ylim(ymin, ymax)
        mean = round(inventory_levels_dataframes[k]["level"].mean(), 2)
        ax = plt.gca()
        ax.text(0, ymax - ymax*0.1, 'mean levels = ' + str(mean) + " kg", style='italic',
            bbox={'facecolor': 'red', 'alpha': 1, 'pad': 10},
            verticalalignment='top', horizontalalignment='left',)
        ax.set_xlabel("time in hours")
        ax.set_ylabel("inventory levels in kg")
    
    inventory_level_total_first_weeks = inventory_level_total_df[inventory_level_total_df < 5*168]
    inventory_level_total_first_weeks.plot(kind = "line", x = "time", y = "level", label = "week 1 to 5").set_ylim(ymin, ymax)
    plt.gca().set_xlabel("time in hours")
    plt.gca().set_ylabel("inventory levels in kg")
    
    inventory_level_total_last_weeks = inventory_level_total_df[inventory_level_total_df > 8904-5*168]
    inventory_level_total_last_weeks.plot(kind = "line", x = "time", y = "level", label = "week 48 to 53").set_ylim(ymin, ymax)
    plt.gca().set_xlabel("time in hours")
    plt.gca().set_ylabel("inventory levels in kg")