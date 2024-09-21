import pandas as pd
import gzip
import os

# Chemins des fichiers locaux
fichiers = [
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\bybit_history\2024\ETH\ETHUSDT_60_2024-02-01_2024-02-29.csv.gz',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\bybit_history\2024\ETH\ETHUSDT_60_2024-03-01_2024-03-31.csv.gz'
]

# Fonction pour lire et décompresser un fichier gzip
def lire_et_decompresser(fichier):
    noms_colonnes = ['Time','open','high','low','close','volume']
    with gzip.open(fichier, 'rt') as f:
        df = pd.read_csv(f, names=noms_colonnes, header=0)  # header=0 indique que la première ligne contient déjà les en-têtes et sera remplacée
    return df

# Lire, décompresser, et concaténer les DataFrames
df_concatenes = pd.concat([lire_et_decompresser(fichier) for fichier in fichiers], ignore_index=True)

# Sauvegarder le DataFrame concaténé dans un nouveau fichier CSV
df_concatenes.to_csv('./2024/ETH/ETHUSDT_bybit2024.csv', index=False)

print("Les fichiers ont été lus, décompressés, et concaténés avec succès.")
