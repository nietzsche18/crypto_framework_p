#coding: utf-8
#source activate py38

'''
L'objectif de ce script est de mesurer les performances d'une stratégie breakout 
Pour l'instant, ça ne calcule qu'une perf après une certaine période lors d'un breakout 
'''

import requests
import datetime
import pandas as pd
import numpy as np
import time


# --------- VARIABLES ---------

coin = 'WIFUSDT'
date_debut = '2023-01-01 00:00:00'
date_fin = datetime.datetime.now()

# BYBIT

def get_info():
    url = 'https://api.bybit.com/v5/market/instruments-info?category={}'.format('linear')
    data = requests.get(url).json()
    print(data)

get_info()

def get_history_bybit(ticker, start, limit=1000):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start))*1000)
    end_date = start + 5731200000
    url = 'https://api.bybit.com/v5/market/kline?category={}&symbol={}&limit={}&interval={}&end={}'.format('linear', ticker, limit, 60, end_date)
    columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'turnover']
    data = requests.get(url).json()
    df = pd.DataFrame(data['result']['list'], columns=columns)
    df.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in df.time]
    #df = df[columns]
    df = df.sort_values('time')
    return df

def get_latest_data_bybit(ticker):
    df = pd.DataFrame()
    start_date = pd.to_datetime(date_debut)  # Convertir en objet datetime

    while True:
        new_data = get_history_bybit(ticker, start=start_date.strftime('%Y-%m-%d %H:%M:%S'))
        print(new_data)
        if not start_date.date() >= date_fin.date():
            df = pd.concat([df, new_data])            
        else:
            break
        start_date += datetime.timedelta(milliseconds=5731200000)
        time.sleep(1)  # Pause pour éviter de surcharger l'API

    df = df.drop_duplicates()
    print(df)
    return df


#df = get_latest_data_bybit(coin)

def main(df):
    # Assurez-vous que les colonnes sont de type float
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    # Calcul des maximums sur 24h et 7 jours glissants
    df['24h_high'] = df['high'].shift(1).rolling(window=24).max()
    df['breakout_24h'] = df['high'] > df['24h_high'] 

    df['7d_high'] = df['high'].shift(1).rolling(window=7*24).max()   
    df['breakout_7d'] = df['high'] > df['7d_high']

    # Calcul de la performance après un breakout sur 24h
    df['perf_break_h1'] = np.where(df['breakout_24h'], (df['close'].shift(-1) - df['24h_high']) / df['24h_high'], np.nan)

    # Affichage des résultats
    print(df[['24h_high', 'breakout_24h', 'perf_break_h1']])
    

#main(df)