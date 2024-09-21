import pandas as pd
import requests 
import json
import csv
import os
from pybit.unified_trading import HTTP


def get_coinapi():
    # coinAPI
    api_key = '5A09F3B1-448B-4400-93B5-F6196F039E3B'

    #url = 'https://rest.coinapi.io/v1/symbols/BINANCEFTS' # liste les data pour Binance FUTURES (USDT)
    #url = "https://rest.coinapi.io/v1/orderbooks/BINANCEFTS_PERP_BTC_USDT/history?time_start=2023-01-01T00:00:00&period_id=1HRS"
    url = 'https://rest.coinapi.io/v1/orderbooks/BINANCEFTS_PERP_BTC_USDT/depth/current?limit_levels=100'

    payload={}
    headers = {
    'Accept': 'text/plain',
    'X-CoinAPI-Key': api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.json())
    """
    for el in response.json():
        print(el['time_exchange'])
    """


liste_pairs = ['BTCUSDT', 'ETHUSDT', 'TIAUSDT']

def get_orderbook(symbol):
    session = HTTP(testnet=True)
    data = session.get_orderbook(
        category="linear",
        symbol=symbol,
    )
 
    # Chemin du fichier CSV
    file_path = './data/order_book/'+symbol+'.csv'

    # Vérifier si le fichier existe déjà pour décider d'ajouter les en-têtes ou non
    file_exists = os.path.isfile(file_path)

    # Création ou mise à jour du fichier CSV
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Ajouter les en-têtes seulement si le fichier est nouveau
        if not file_exists:
            writer.writerow(['Type', 'Price', 'Amount', 'Timestamp'])
        
        # Données de la liste 'b'
        for item in data['result']['b']:
            writer.writerow(['b'] + item + [data['result']['ts']])
        
        # Données de la liste 'a'
        for item in data['result']['a']:
            writer.writerow(['a'] + item + [data['result']['ts']])

    print("Les données ont été ajoutées")


for pair in liste_pairs:
    get_orderbook(pair)