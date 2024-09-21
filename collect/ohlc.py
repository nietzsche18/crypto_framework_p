#coding: utf-8
#source activate py35

import requests
import datetime
import pandas as pd
import numpy as np
import time
import os


def get_binance_data_request_(ticker, interval='1h', limit=1000, start='2023-01-01 00:00:00'):
    """
    interval: str tick interval - 4h/1h/1d ...
    """
    print('nouvelle requête qui débute au ', str(start))
    columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore']
    start = int(datetime.datetime.timestamp(pd.to_datetime(start))*1000)
    url = 'https://www.binance.com/api/v3/klines?symbol={}&interval={}&limit={}&startTime={}'.format(ticker, interval, limit, start)
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=columns)
    df.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in df.open_time]
    usecols=['open', 'high', 'low', 'close', 'volume', 'qav','num_trades','taker_base_vol','taker_quote_vol']
    df = df[usecols]
    return df




def get_ohlc(ticker, interval='1h'):
    csv_file = './data/1hour/ohlc_btc_2023.csv'
    df = pd.DataFrame()

    # Vérifie si le fichier CSV existe
    if os.path.exists(csv_file):
        # Si le fichier existe, lire le dernier timestamp
        df = pd.read_csv(csv_file, index_col=0)
        start_date = df.index[-1]
        print('Le fichier existe et se termine le ' , start_date)
    else:
        # Sinon, définir la date de début à une date antérieure
        start_date = '2023-01-01 00:00:00'

    today = datetime.datetime.now()

    while True:
        print(df)
        new_data = get_binance_data_request_(ticker, interval, start=start_date)
        
        # Vérifie si new_data n'est pas vide
        if not new_data.empty:
            df = pd.concat([df, new_data])

            # Convertit la dernière date en df en datetime
            start_date = datetime.datetime.strptime(df.index[-1], '%Y-%m-%d %H:%M:%S')

            # Interrompt la boucle si la dernière date en df est aujourd'hui
            if start_date.date() >= today.date():
                break

        time.sleep(10)


    df.to_csv(csv_file, index=True)



