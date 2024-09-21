#coding: utf-8
#source activate py39

import pandas as pd
import numpy as np


def main(tf):
    source_data = './data/'+ tf +'/ohlc_btc_2023.csv'
    df = pd.read_csv(source_data, index_col=0)
    df = df.drop_duplicates()

    df['t'] = df.index
    df['previous_low'] = df['low'].shift(1)
    df['previous_open'] = df['open'].shift(1)
    df['week_day'] = pd.to_datetime(df['t']).dt.day_name()
    df['week_end'] = df['week_day'].isin(['Saturday', 'Sunday'])

    # VOLUME METRICS
    df['dollar_volume'] = df['close']*df['volume']
    df['7d_dollar_volume_rank'] = pd.to_numeric(df['dollar_volume'], errors='coerce').rolling(window=24*7, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*7), raw=False)
    df['30d_dollar_volume_rank'] = pd.to_numeric(df['dollar_volume'], errors='coerce').rolling(window=24*30, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*30), raw=False)

    df['average_dollar_volume_per_trade'] = df['dollar_volume'] / df['num_trades']
    df['7d_volume_per_trade_rank'] = pd.to_numeric(df['average_dollar_volume_per_trade'], errors='coerce').rolling(window=24*7, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*7), raw=False)
    df['30d_volume_per_trade_rank'] = pd.to_numeric(df['average_dollar_volume_per_trade'], errors='coerce').rolling(window=24*30, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*30), raw=False)
    df['average_dollar_volume_24h'] = df['dollar_volume'].rolling(window=24*10).mean()

    df['relative_volume'] = df['dollar_volume'] / df['average_dollar_volume_24h']
    df['24h_volume_rank'] = pd.to_numeric(df['dollar_volume'], errors='coerce').rolling(window=24, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24), raw=False)
    df['30d_volume_rank'] = pd.to_numeric(df['dollar_volume'], errors='coerce').rolling(window=24*30, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*30), raw=False)


   # CHANGES %  

    # Calcul du changement sur l'heure (%)
    df['h1_chg'] = ((df['close'] - df['open']) / df['open']) * 100
    df['24h_h1_chg_rank'] = pd.to_numeric(df['h1_chg'], errors='coerce').rolling(window=24, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24), raw=False)
    df['30d_h1_chg_rank'] = pd.to_numeric(df['h1_chg'], errors='coerce').rolling(window=24*30, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*30), raw=False)

    # Changement sur les 3 dernières heures (%)
    df['prev_3h_chg'] = df['close'].pct_change(periods=3) * 100

    # Changement sur les 24 dernières heures (%)
    df['prev_24h_chg'] = df['close'].pct_change(periods=24) * 100

    # Changement sur l'heure d'après
    df['next_hour_close'] = df['close'].shift(-1)
    df['next_hour_chg'] = ((df['close'].shift(-1) - df['close']) / df['close']) * 100

    # Changement maximum à la hausse sur l'heure d'après
    df['next_hour_high'] = df['high'].shift(-1)
    df['next_hour_high_chg'] = ((df['high'].shift(-1) - df['close']) / df['close']) * 100

    # Changement maximum à la baisse sur l'heure d'après
    df['next_hour_low'] = df['low'].shift(-1)
    df['next_hour_low_chg'] = ((df['low'].shift(-1) - df['close']) / df['close']) * 100

    # Changement sur les 3h d'après
    df['next_3h_chg'] = ((df['close'].shift(-3) - df['close']) / df['close']) * 100

    # Changement maximum à la hausse sur les 3h d'après
    df['next_3h_high_chg'] = ((df['high'].rolling(window=3).max().shift(-3) - df['close']) / df['close']) * 100

    # Changement maximum à la baisse sur les 3h d'après
    df['next_3h_low_chg'] = ((df['low'].rolling(window=3).min().shift(-3) - df['close']) / df['close']) * 100


    # FUNDINGS
    csv_file = './data/'+ tf +'/btc_2023_aggregated_fundings.csv'
    df_fundings = pd.read_csv(csv_file, index_col=0)
    df = df.join(df_fundings['c'].rename('fundings'))
    df['fundings_rank'] = pd.to_numeric(df['fundings'], errors='coerce').rolling(window=24*30, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*30), raw=False)


    # LIQUIDATIONS
    csv_file = './data/'+ tf +'/btc_2023_binance_liquidation.csv'
    df_liq = pd.read_csv(csv_file, index_col=0)
    df = df.join(df_liq['l'].rename('liquidation_longs'))
    df['liquidation_longs_rank'] = pd.to_numeric(df['liquidation_longs'], errors='coerce').rolling(window=24*30, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*30), raw=False)
    df = df.join(df_liq['s'].rename('liquidation_shorts'))
    df['liquidation_shorts'] = df['liquidation_shorts'].fillna(0)
    df['liquidation_shorts_rank'] = pd.to_numeric(df['liquidation_shorts'], errors='coerce').rolling(window=24*30, min_periods=1).apply(lambda x: categorize_based_on_percentile(x, 24*30), raw=False)


    # LONG SHORT
    csv_file = './data/'+ tf +'/btc_2023_binance_long_short.csv'
    df_long = pd.read_csv(csv_file, index_col=0)
    df = df.join(df_long['l'].rename('long_%'))
    df['longs_1h_chg%'] = ((df['long_%'] - df['long_%'].shift(1)) / df['long_%'].shift(1)) * 100
    df['longs_24h_chg%'] = df['long_%'].pct_change(periods=24) * 100


    # OPEN INTEREST
    csv_file = './data/'+ tf +'/btc_2023_binance_oi.csv'
    df_oi = pd.read_csv(csv_file, index_col=0)
    df = df.join(df_oi['c'].rename('open_interest'))
    df['oi_1h_chg%'] = ((df['open_interest'] - df['open_interest'].shift(1)) / df['open_interest'].shift(1)) * 100
    df['oi_24h_chg%'] = df['open_interest'].pct_change(periods=24) * 100   

 
    # BREAKOUT OF HIGHS

    # breakout 24h : break du high sur 24h 
    df['24h_high'] = df['high'].shift(1).rolling(window=24).max()
    df['24h_highest_close'] = df['close'].shift(1).rolling(window=24).max()
    df['breakout_24h'] = df['high'] > df['24h_high'] 
    df['closed_breakout_24h'] = df['close'] > df['24h_high'] 
    df['high_from_24h_high'] = (df['high'] - df['24h_high']) / df['24h_high'] # utile en cas de breakout : performance entre le breakout et le high sur l'heure en cours, où pour voir si on est proche d'un breakout 

    # breakout 7j
    df['7d_high'] = df['high'].shift(1).rolling(window=7*24).max()   
    df['7d_highest_close'] = df['close'].shift(1).rolling(window=7*24).max()   
    df['breakout_7d'] = df['high'] > df['7d_high']
    df['closed_breakout_7d'] = df['close'] > df['7d_high'] 
    df['high_from_7d_high'] = (df['high'] - df['7d_high']) / df['7d_high'] # utile en cas de breakout : performance entre le breakout et le high sur l'heure en cours

    # breakout 14j
    df['14d_high'] = df['high'].shift(1).rolling(window=14*24).max()   
    df['14d_highest_close'] = df['close'].shift(1).rolling(window=14*24).max()   
    df['closed_breakout_14d'] = df['close'] > df['14d_high'] 
    df['breakout_14d'] = df['high'] > df['14d_high']
    df['high_from_14d_high'] = (df['high'] - df['14d_high']) / df['14d_high'] # utile en cas de breakout : performance entre le breakout et le high sur l'heure en cours

    # breakout 30j
    df['30d_high'] = df['high'].shift(1).rolling(window=30*24).max()   
    df['breakout_30d'] = df['high'] > df['30d_high']
    df['high_from_30d_breakout'] = (df['high'] - df['30d_high']) / df['30d_high']

    # breakout of n-period : nouveau plus haut de n jours 
    def calculer_n_hours_breakout(df, value):
        liste = df[value]
        max_diffs = []  # Liste pour stocker le maximum de i-j pour chaque élément
        i = 1
        for item in liste:
            max_diff = 0  # Initialiser le maximum de i-j pour l'élément actuel
            j = i - 2
            while j >= 0:
                if item > liste[j]:
                    max_diff = i-j-1  # Mettre à jour le maximum de i-j si nécessaire
                    j = j - 1
                else:
                    j = -1
            max_diffs.append(max_diff)  # Ajouter le maximum de i-j pour cet élément à la liste
            i = i + 1
        df['n_hours_breakout_' + value] = max_diffs

    calculer_n_hours_breakout(df, 'high')
    calculer_n_hours_breakout(df, 'close')

    df['closed_green'] = df['open'] < df['close']
    df['mainly_full_green'] =  (df['close'] - df['open']) / (df['high'] - df['low']) > 0.7


    # VOLATILITE
    df['sigma_previous_period'] = df['close'].rolling(20).std().shift(1)
    df['sigma'] = df['close'].rolling(20).std()

    # MM
    df['SMA20_h1'] = df['close'].rolling(window=20).mean()
    df['SMA50_h1'] = df['close'].rolling(window=50).mean()
    df['SMA20_h4'] = df['close'].rolling(window=20*4).mean()
    df['SMA50_h4'] = df['close'].rolling(window=50*4).mean()
    df['EMA7_d'] = df['close'].ewm(span=7*24, adjust=False).mean()
    df['SMA20_d'] = df['close'].rolling(window=20*24).mean()
    df['SMA50_d'] = df['close'].rolling(window=50*24).mean()

    def calculate_duration_above_ma(df, ma_column):
        duration = [0] * len(df)  # Initialiser une liste de zéros de la même longueur que le DataFrame
        for i in range(1, len(df)):
            # Si le cours de clôture est supérieur à la moyenne mobile, incrémenter le compteur
            if df['close'].iloc[i] > df[ma_column].iloc[i]:
                duration[i] = duration[i-1] + 1
            # Sinon, réinitialiser le compteur
            else:
                duration[i] = 0
        return duration

    df['duration_above_SMA20_h1'] = calculate_duration_above_ma(df, 'SMA20_h1')
    df['duration_above_SMA50_h1'] = calculate_duration_above_ma(df, 'SMA50_h1')
    df['duration_above_SMA20_h4'] = calculate_duration_above_ma(df, 'SMA20_h4')
    df['duration_above_SMA50_h4'] = calculate_duration_above_ma(df, 'SMA50_h4')
    df['duration_above_EMA7_d'] = calculate_duration_above_ma(df, 'EMA7_d')
    df['duration_above_SMA20_d'] = calculate_duration_above_ma(df, 'SMA20_d')
    df['duration_above_SMA50_d'] = calculate_duration_above_ma(df, 'SMA50_d')

    # SAVE

    print(df)
    df.to_csv('./data/btc_fulldata.csv', index=True)
    df.to_csv('../backtest/data/dataset/btc_fulldata.csv', index=True)

def categorize_based_on_percentile(window, period=24):
    # Vérifier si la fenêtre contient suffisamment de données; sinon, retourner NaN ou une valeur par défaut
    if len(window.dropna()) < period:
        return np.nan  # ou une autre valeur numérique par défaut
    else:
        # Calculer les percentiles 30e et 70e
        p30 = np.percentile(window, 30)
        p70 = np.percentile(window, 70)
        
        # Fonction pour catégoriser une valeur unique basée sur les percentiles
        def categorize_value(value):
            if value > p70:
                return 2  # au lieu de "high"
            elif value < p30:
                return 0  # au lieu de "low"
            else:
                return 1  # au lieu de "middle"
        
        # Appliquer la fonction de catégorisation à la dernière valeur de la fenêtre
        return categorize_value(window.iloc[-1])
    
#df['category'] = df['your_column'].rolling(window=24, min_periods=1).apply(categorize_based_on_percentile, raw=False)



main('1hour')


