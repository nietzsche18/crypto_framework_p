import pandas as pd
from datetime import datetime
import requests 
import json
import csv
from google.cloud import bigquery
import os
from pybit.unified_trading import HTTP


liste_pairs = ['BTCUSDT', 'ETHUSDT', 'TIAUSDT', 'ARBUSDT', 'SOLUSDT', 'AVAXUSDT', 'ADAUSDT', 'SANDUSDT', 'BNBUSDT', 'XRPUSDT', 'SUIUSDT', 'DOGEUSDT', 'ATOMUSDT']

# Initialiser le client BigQuery
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client()

# Nom du dataset et de la table
dataset_id = 'orderbook'

# Initialiser le job
job_config = bigquery.LoadJobConfig()
job_config.autodetect = True
job_config.write_disposition = "WRITE_APPEND"


def get_orderbook(symbol):
    session = HTTP(testnet=True)
    data = session.get_orderbook(
        category="linear",
        symbol=symbol,
        limit=200
    )

    # Chemin complet de la table
    table_ref = client.dataset(dataset_id).table(symbol)

    # Préparer les données pour BigQuery
    rows_to_insert = []

    # Données de la liste 'b'
    for item in data['result']['b']:
        ts = datetime.fromtimestamp(data['result']['ts']/1000).isoformat()
        rows_to_insert.append({'side':'b', 'price': item[0], 'amount': item[1], 'timestamp': ts})

    # Données de la liste 'a'
    for item in data['result']['a']:
        ts = datetime.fromtimestamp(data['result']['ts']/1000).isoformat()
        rows_to_insert.append({'side':'a', 'price': item[0], 'amount': item[1], 'timestamp': ts})


    # Charger les données dans BigQuery
    job = client.load_table_from_json(rows_to_insert, table_ref, job_config=job_config)
    job.result()
    if job.errors:
        print("Erreurs rencontrées lors du chargement des données :")
        print(job.errors)
    else:
        print(f"Les données ont été chargées avec succès dans {symbol}.")



for pair in liste_pairs:
    print(pair)
    get_orderbook(pair)