#coding: utf-8
#source activate py38

from dotenv import load_dotenv
import os

load_dotenv()  # Charger les variables d'environnement depuis le fichier .env

import requests
import datetime
import pandas as pd
import numpy as np
import time
import json
import os
from ohlc import get_ohlc 


"""
- FUNDINGS
- OPEN INTEREST
- LIQUIDATIONS
- LONG SHORT RATIO
"""





# ---------------- GENERAL ------------------------------------------------------

api_coinalyze = os.getenv('API_COINALYZE')


def save_data(df, tf, exchange, data_type):
    # Affichage des premières lignes du DataFrame fusionné
    print(df.head())
    csv_file = './data/'+ tf + '/btc_2023_' + exchange + '_' + data_type + '.csv'
    df.to_csv(csv_file, index=True)

def test():
    url = 'https://api.coinalyze.net/v1/future-markets?api_key='+api_coinalyze
    data = requests.get(url).json()
    for zboub in data:
        if zboub['exchange'] == 'K' and zboub['base_asset'] == 'BTC':
            print(zboub)
    #print(json.dumps(data, indent=4))

#test()

def get_latest_data(ticker, tf, exchange, data_type, function_for_new_data):
    csv_file = './data/'+ tf + '/btc_2023_' + exchange + '_' + data_type + '.csv'
    print('retrieving data for ', csv_file)
    df = pd.DataFrame()

    df_lines = 0

    # Vérifie si le fichier CSV existe
    if os.path.exists(csv_file):
        # Si le fichier existe, lire le dernier timestamp
        df = pd.read_csv(csv_file, index_col=0)
        start_date = df.index[-1]
        df = df.iloc[:-2]
        df_lines = len(df)
        print('Le fichier existe et se termine le ' , start_date)
    else:
        # Sinon, définir la date de début à une date antérieure
        start_date = '2023-01-01 00:00:00'

    today = datetime.datetime.now()


    while True:
        new_data = function_for_new_data(ticker, tf, start_date)
        
        # Vérifie si new_data n'est pas vide
        if not new_data.empty:
            df = pd.concat([df, new_data])

            # Convertit la dernière date en df en datetime
            latest_date = datetime.datetime.strptime(df.index[-1], '%Y-%m-%d %H:%M:%S')

            # Interrompt la boucle si la dernière date en df est aujourd'hui
            if latest_date.date() >= today.date():
                break

        time.sleep(10)

    print(df)
    new_lines = len(df) - df_lines
    print(new_lines ,' nouvelles lignes')
    save_data(df, tf, exchange, data_type)


# ---------------- FUNDINGS ------------------------------------------------------


def get_fundings(ticker, tf, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start)))
    to = int(datetime.datetime.now().timestamp())
    url = 'https://api.coinalyze.net/v1/funding-rate-history?api_key={}&symbols={}&interval={}&from={}&to={}'.format(api_coinalyze, ticker, tf, start, to)
    data = requests.get(url).json()

    df = pd.DataFrame()
    for result in data:
        print(result['symbol'])
        new_df = pd.DataFrame(result['history'])
        new_df.index = [pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S') for x in new_df.t]
        #print(new_df)
        #print(new_df['c'].max())
        df = pd.concat([df, new_df])
    df = df.groupby(level=0).mean()  # Appliquez groupby puis mean sur le DataFrame final
    return df


#get_fundings('BTCUSDT_PERP.A,BTCUSDT.6', '5min', 'binance') # Binance, bybit


# ---------------- OPEN INTEREST ------------------------------------------------------


def get_openinterest(ticker, tf, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start)))
    to = int(datetime.datetime.now().timestamp())
    url = 'https://api.coinalyze.net/v1/open-interest-history?api_key={}&symbols={}&interval={}&from={}&to={}'.format(api_coinalyze, ticker, tf, start, to)
    data = requests.get(url).json()[0]['history']
    df = pd.DataFrame(data)
    df.index = [pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S') for x in df.t]
    #print(df)
    return df
    # il faudrait ajouter une loop qui permet de ne récupérer que la suite 

#get_openinterest('BTCUSDT_PERP.A', '5min', 'binance') # Binance
#get_openinterest('BTCUSDT_PERP.6', 'bybit') # Bybit



# ---------------- LIQUIDATION ------------------------------------------------------

# l = long liquidations, s = short liquidations

def get_liquidations(ticker, tf, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start)))
    today = int(datetime.datetime.now().timestamp())
    url = 'https://api.coinalyze.net/v1/liquidation-history?api_key={}&symbols={}&interval={}&from={}&to={}&convert_to_usd=true'.format(api_coinalyze, ticker, tf, start, today)
    data = requests.get(url).json()[0]['history']
    df = pd.DataFrame(data)
    df.index = [pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S') for x in df.t]
    return df


#get_liquidations('BTCUSDT_PERP.A', '5min', 'binance') # Binance



# ---------------- LONG / SHORT RATIO ------------------------------------------------------

def get_long_short(ticker, tf, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start)))
    today = int(datetime.datetime.now().timestamp())
    url = 'https://api.coinalyze.net/v1/long-short-ratio-history?api_key={}&symbols={}&interval={}&from={}&to={}'.format(api_coinalyze, ticker, tf, start, today)
    data = requests.get(url).json()[0]['history']
    df = pd.DataFrame(data)
    df.index = [pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S') for x in df.t]
    return df


#get_long_short('BTCUSDT_PERP.A', '5min','binance') # Binance




# ---------------- MAIN FUNCTIONS  ------------------------------------------------------

get_ohlc('BTCUSDT')

get_latest_data('BTCUSDT_PERP.A', '1hour', 'binance', 'oi', get_openinterest)
get_latest_data('BTCUSDT_PERP.A', '1hour', 'binance', 'long_short', get_long_short)
get_latest_data('BTCUSDT_PERP.A', '1hour', 'binance', 'liquidation', get_liquidations)
get_latest_data('BTCUSDT_PERP.A,BTCUSDT.6', '1hour', 'aggregated', 'fundings', get_fundings)


get_latest_data('BTCUSDT_PERP.A', '5min', 'binance', 'long_short', get_long_short)
get_latest_data('BTCUSDT_PERP.A', '5min', 'binance', 'oi', get_openinterest)
get_latest_data('BTCUSDT_PERP.A', '5min', 'binance', 'liquidation', get_liquidations)
get_latest_data('BTCUSDT_PERP.A,BTCUSDT.6', '5min', 'aggregated', 'fundings', get_fundings)


