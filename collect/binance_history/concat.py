import pandas as pd
import zipfile
import os

# Chemins des fichiers locaux
fichiers = [
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-04.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-05.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-06.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-07.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-08.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-09.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-10.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-11.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2020-12.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2021-01.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2021-02.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2021-03.zip',
    r'C:\Users\b.bellity_ext\Desktop\data_analysis\crypto_framework\collect\binance_history\BTCUSDT-1h-2021-04.zip'
]

# Fonction pour lire et décompresser un fichier zip
def lire_et_decompresser(fichier):
    noms_colonnes = ['Time','open','high','low','close','volume','close_time','quote_volume','count','taker_buy_volume','taker_buy_quote_volume','ignore']
    with zipfile.ZipFile(fichier, 'r') as z:
        # Supposons que chaque fichier zip contient un seul fichier CSV
        nom_fichier_csv = z.namelist()[0]  # Obtient le nom du premier fichier dans le zip
        with z.open(nom_fichier_csv) as f:
            df = pd.read_csv(f, names=noms_colonnes, header=0)  # header=0 indique que la première ligne contient déjà les en-têtes et sera remplacée
    return df

# Lire, décompresser, et concaténer les DataFrames
df_concatenes = pd.concat([lire_et_decompresser(fichier) for fichier in fichiers], ignore_index=True)

# Sauvegarder le DataFrame concaténé dans un nouveau fichier CSV
df_concatenes.to_csv('BTCUSDT_binance.csv', index=False)

print("Les fichiers ont été lus, décompressés, et concaténés avec succès.")
