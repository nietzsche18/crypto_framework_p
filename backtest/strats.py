#coding: utf-8
#source activate py39

# ce fichier teste les stratégies d'entrées / sorties 

import pandas as pd
import itertools


# --------- A CODER ---------------------------------------


SL_conditions = [
    'low < entry*0.99',
    'half of (previous) candle',
    'low of previous candle',
    'low of breakout candle',
    'low of daily candle',
    'previous lower low (with lows)',
    'previous lower low (with closes)',
    'close below 20SMA',
    'first red candle'
]

TP_conditions = [
    '2R',
    'fibo',
    'touch BB'

]





# ------------- ENTRIES -------------------------

def entry_close(row):
    return row['close'] 

def entry_breakout(row):
    return row['30d_high'] 


# ------------- STOP LOSSES -------------------------

def sl_previous_low(row):
    return row['previous_low']  

def sl_low(row):
    return row['low']  

def sl_half_low(row):
    return (row['low']+row['close'])/2

def make_sl_x_percent(x):
    def sl_x_percent(row):
        return row['close'] * (1 - x / 100)
    sl_x_percent.__name__ = f'sl_x_percent_{x}'
    sl_x_percent.x_value = x  # Stocker la valeur de x
    return sl_x_percent

def make_sl_x_sigma(x):
    def sl_x_sigma(row):
        return row['close']-row['sigma']*x
    sl_x_sigma.__name__ = f'sl_x_sigma_{x}'
    sl_x_sigma.x_value = x  # Stocker la valeur de x
    return sl_x_sigma



# ------------- TAKE PROFITS -------------------------
def make_tp_XR(r):
    def tp_XR(row, entry_price, stop_loss):
        return entry_price + r * (entry_price - stop_loss)
    tp_XR.__name__ = f'tp_XR_{r}'
    tp_XR.r_value = r  # Stocker la valeur de r
    return tp_XR

def make_tp_xpercent(x):
    def tp_xpercent(row, entry_price, stop_loss):
        return entry_price*(1+x/100)
    tp_xpercent.__name__ = f'tp_xpercent_{x}'
    tp_xpercent.x_value = x  # Stocker la valeur de x
    return tp_xpercent

# not fixed 
def tp_bb(row, entry_price, stop_loss, x):
    return entry_price*(1+x/100) # à corriger


def make_tp_x_sigma(x):
    def tp_x_sigma(row, entry_price=None, stop_loss=None):
        return row['close']+row['sigma']*x
    tp_x_sigma.__name__ = f'tp_x_sigma_{x}'
    tp_x_sigma.x_value = x  # Stocker la valeur de x
    return tp_x_sigma

# first red candle



# ------------- LIST OF STRATEGIES -------------------------


# LISTE BIG GRID SEARCH

entry_strategies = [entry_close]  
sl_strategies = [sl_previous_low, sl_low, sl_half_low] + [make_sl_x_percent(x) for x in [1, 2, 3, 4, 5]] + [make_sl_x_sigma(x) for x in [1, 1.5, 2, 2.5, 3]]
tp_strategies = [make_tp_XR(x) for x in [1, 1.5, 2, 2.5, 3, 4, 5, 7, 10]] + [make_tp_xpercent(x) for x in [1, 2, 3, 5, 7, 10, 12.5, 15]] + [make_tp_x_sigma(x) for x in [1, 2, 3, 4, 5]]
















#

#
