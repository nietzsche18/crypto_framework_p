#coding: utf-8

import pandas as pd
import mplfinance as mpf

# Charger les données (ajustez le chemin vers votre fichier)
file_path = './btc_fulldata.csv'
data = pd.read_csv(file_path)

# Convertir la colonne de temps en datetime et la définir comme index
data['Unnamed: 0'] = pd.to_datetime(data['Unnamed: 0'])
data = data.set_index('Unnamed: 0')

# Filtrer les données pour une période plus courte si nécessaire
data = data['2023-01-09':'2023-01-10']

# Filtrer les colonnes nécessaires pour mplfinance
data_for_mpf = data[['open', 'high', 'low', 'close', 'volume']]

# Identifier les points de breakout
breakouts_values = data[data['breakout_7d'] == True]['high'].reindex(data_for_mpf.index) * 1.01

# Créer un style personnalisé pour mplfinance
mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
s = mpf.make_mpf_style(marketcolors=mc)

# Préparer les points de breakout pour le traçage
apd = mpf.make_addplot(breakouts_values, type='scatter', markersize=50, marker='^', color='blue')

# Tracer les bougies avec les points de breakout
mpf.plot(data_for_mpf, type='candle', style=s, addplot=apd, volume=True, figratio=(12,8), title="BTC Candles avec Breakouts 7d", ylabel='Prix (USD)', ylabel_lower='Volume', warn_too_much_data=10000)
