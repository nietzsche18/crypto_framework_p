#coding: utf-8
#source activate py35

import requests
import datetime
import pandas as pd
import numpy as np
import time
import json


"""
- FUNDINGS
- OPEN INTEREST
- LONG SHORT RATIO
"""


# ---------------- GENERAL ------------------------------------------------------



def save_data(df, tf, exchange, data_type):
    # Affichage des premières lignes du DataFrame fusionné
    print(df.head())
    csv_file = './data/'+ tf + '_btc_2023_' + exchange + '_' + data_type + '.csv'
    df.to_csv(csv_file, index=True)



# ---------------- FUNDINGS ------------------------------------------------------

# à refaire à partir de l'API coinalyze 

# BINANCE

def get_funding_rate_history_binance(ticker, limit=1000, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start))*1000)
    url = 'https://fapi.binance.com/fapi/v1/fundingRate?symbol={}&limit={}&startTime={}'.format(ticker, limit, start)
    columns = ['symbol', 'fundingTime', 'fundingRate', 'markPrice']
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=columns, dtype=np.float)
    df.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in df.fundingTime]
    usecols=['symbol', 'fundingTime', 'fundingRate']
    df = df[usecols]

     # Assurez-vous que l'index est unique
    df = df[~df.index.duplicated(keep='first')]
 
    # Remise à l'échelle du DataFrame df_funding_rate pour avoir une entrée toutes les heures, en remplissant vers l'avant la dernière valeur connue
    df.index = pd.DatetimeIndex(df.index)
    df['fundingRate'] = df['fundingRate'].resample('H').ffill()
 
    return df

# boucle pour rechercher l'historique 1000 par 1000
def get_latest_data_binance(ticker, interval='1h'):
    df = pd.DataFrame()
    today = datetime.datetime.now()

    while True:
        if df.empty:
            start_date = '2023-01-01 00:00:00'
        else:
            start_date = df.index[-1]

        print('retrieving data from ', start_date)
        new_data = get_funding_rate_history_binance(ticker, start=start_date)
        
        # Check if new_data is not empty
        if not new_data.empty:
            df = pd.concat([df, new_data])

            # Convert the latest date in df to datetime
            latest_date = datetime.datetime.strptime(df.index[-1], '%Y-%m-%d %H:%M:%S')

            # Break the loop if the latest date in df is today
            if latest_date.date() >= today.date():
                break
        
        time.sleep(10)
    return df

#df = get_latest_data_binance('BTCUSDT')
#save_data(df, "h1", "binance", "funding")


# BYBIT
def get_funding_rate_history_bybit(ticker, limit=200, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start))*1000)
    end_date = start + 5731200000
    url = 'https://api.bybit.com/v5/market/funding/history?category={}&symbol={}&limit={}&endTime={}'.format('linear', ticker, limit, end_date)
    columns = ['fundingRate', 'fundingRateTimestamp', 'symbol']
    data = requests.get(url).json()
    df = pd.DataFrame(data['result']['list'], columns=columns, dtype=np.float)
    df.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in df.fundingRateTimestamp]
    df = df[columns]
    df = df.sort_values('fundingRateTimestamp')
    return df

def get_latest_data_bybit(ticker, interval='1h'):
    df = pd.DataFrame()
    today = datetime.datetime.now()

    while True:
        print(df)
        if df.empty:
            start_date = '2023-01-01 00:00:00'
        else:
            start_date = df.index[-1]

        new_data = get_funding_rate_history_bybit(ticker, start=start_date)
        
        # Check if new_data is not empty
        if not new_data.empty:
            df = pd.concat([df, new_data])

            # Convert the latest date in df to datetime
            latest_date = datetime.datetime.strptime(df.index[-1], '%Y-%m-%d %H:%M:%S')

            # Break the loop if the latest date in df is today
            if latest_date.date() >= today.date():
                break
        
        time.sleep(10)
    df = df.drop_duplicates()
    return df

#df = get_latest_data_bybit('BTCUSDT')
#print(df)


# ---------------- OPEN INTEREST ------------------------------------------------------


def get_openinterest(ticker, tf, exchange, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start)))
    to = int(datetime.datetime.now().timestamp())
    url = 'https://api.coinalyze.net/v1/open-interest-history?api_key={}&symbols={}&interval={}&from={}&to={}'.format(api_coinalyze, ticker, tf, start, to)
    data = requests.get(url).json()[0]['history']
    df = pd.DataFrame(data)
    df.index = [pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S') for x in df.t]
    print(df)
    save_data(df, "h1", exchange, 'oi')
    # il faudrait ajouter une loop qui permet de ne récupérer que la suite 

get_openinterest('BTCUSDT_PERP.A', '1hour', 'binance') # Binance
#get_openinterest('BTCUSDT_PERP.6', 'bybit') # Bybit



# ---------------- LONG / SHORT RATIO ------------------------------------------------------

def get_long_short(ticker, exchange, start='2023-01-01 00:00:00'):
    start = int(datetime.datetime.timestamp(pd.to_datetime(start)))
    today = int(datetime.datetime.now().timestamp())
    url = 'https://api.coinalyze.net/v1/long-short-ratio-history?api_key={}&symbols={}&interval=1hour&from={}&to={}'.format(api_coinalyze, ticker, start, today)
    data = requests.get(url).json()[0]['history']
    df = pd.DataFrame(data)
    df.index = [pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S') for x in df.t]
    print(df)
    save_data(df, "h1", exchange, 'long_short')


#get_long_short('BTCUSDT_PERP.A', 'binance') # Binance


def test():
    url = 'https://api.coinalyze.net/v1/exchanges?api_key='+api_coinalyze
    data = requests.get(url).json()
    print(json.dumps(data, indent=4))

