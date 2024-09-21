#coding: utf-8
#source activate py39

# version avant parallèlisation 

import pandas as pd
from itertools import combinations, product
from strats import entry_strategies, sl_strategies, tp_strategies
import metrics
import time
import random

"""
On a une liste de conditions
On a un GridSearch qui va composer des stratégies sur base de tuple de 3 conditions
On va avoir une classe qui teste ces 3 conditions pour chaque ligne du dataframe 
Pour chaque tuple de 3 conditions, on teste différentes stratégies de sortie (également produites en GridSearch)

"""

# ------ ENTRY CONDITIONS -----------------------------


conditions = {
    'dollar_volume': ['x > 1000000'],
    '7d_dollar_volume_rank': ['x == 2', 'x == 0'],
    '30d_dollar_volume_rank': ['x == 2', 'x == 0'],
    '7d_volume_per_trade_rank': ['x == 2', 'x == 0'],
    '30d_volume_per_trade_rank': ['x == 2', 'x == 0'],
    'relative_volume': ['x > 2', 'x > 3'],
    '30d_volume_rank': ['x == 2'],
    'num_trades': ['x > 150000'],
    'taker_base_vol': ['x > 2500'],
    'taker_quote_vol': ['x > 4e7'],
    'h1_chg': ['x > 0.01', 'x > 0.02', 'x > 0.03', 'x > 0.04'],
    'prev_3h_chg': ['x > 0.01', 'x > 0.02', 'x > 0.03', 'x > 0.04'],
    'prev_24h_chg': ['x > 0.01', 'x > 0.03',  'x > 0.05'],
    '24h_h1_chg_rank': ['x == 2'],
    '30d_h1_chg_rank': ['x == 2'],
    'fundings_rank': ['x == 2', 'x == 1', 'x == 0'],
    'fundings': ['x > 0.01', 'x < 0'],
    'liquidation_longs': ['x > 1000000'],
    'liquidation_shorts': ['x > 1000000'],
    'liquidation_longs_rank': ['x == 2', 'x == 1', 'x == 0'],
    'liquidation_shorts_rank': ['x == 2', 'x == 1', 'x == 0'],
    'long_%': [ 'x > 50', 'x > 60', 'x > 70' 'x < 30', 'x < 40', 'x < 50'],
    'longs_24h_chg%': ['x > 1', 'x > 2', 'x > 3', 'x > 5', 'x < -1', 'x < -2', 'x < -3', 'x < -5'],
    'oi_24h_chg%': ['x > 1', 'x > 2', 'x > 3', 'x > 5', 'x < -1', 'x < -2', 'x < -3', 'x < -5'],
    'breakout_24h': ['x == True'],
    'breakout_7d': ['x == True'],
    'breakout_14d': ['x == True'],
    'breakout_30d': ['x == True'],
    'n_hours_breakout': ['x > 1440', 'x > 4320']
}

conditions_full = {
    'dollar_volume': ['x > 1000000'],
    '7d_dollar_volume_rank': ['x == 2', 'x == 1', 'x == 0'],
    '30d_dollar_volume_rank': ['x == 2', 'x == 1', 'x == 0'],
    '7d_volume_per_trade_rank': ['x == 2', 'x == 1', 'x == 0'],
    '30d_volume_per_trade_rank': ['x == 2', 'x == 1', 'x == 0'],
    'relative_volume': ['x > 2', 'x > 3'],
    '30d_volume_rank': ['x == 2', 'x == 1', 'x == 0'],
    'num_trades': ['x > 150000'],
    'taker_base_vol': ['x > 2500'],
    'taker_quote_vol': ['x > 4e7'],
    'h1_chg': ['x > 0.01', 'x > 0.02', 'x > 0.03', 'x > 0.04'],
    'prev_3h_chg': ['x > 0.01', 'x > 0.02', 'x > 0.03', 'x > 0.04'],
    'prev_24h_chg': ['x > 0.01', 'x > 0.02', 'x > 0.03', 'x > 0.04', 'x > 0.05', 'x > 0.06', 'x > 0.07'],
    '24h_h1_chg_rank': ['x == 2'],
    '30d_h1_chg_rank': ['x == 2'],
    'fundings_rank': ['x == 2', 'x == 1', 'x == 0'],
    'fundings': ['x > 0.01', 'x < 0'],
    'liquidation_longs': ['x > 1000000'],
    'liquidation_shorts': ['x > 1000000'],
    'liquidation_longs_rank': ['x == 2', 'x == 1', 'x == 0'],
    'liquidation_shorts_rank': ['x == 2', 'x == 1', 'x == 0'],
    'long_%': ['x > 30', 'x > 40', 'x > 50', 'x > 60', 'x > 70', 'x > 80', 'x < 30', 'x < 40', 'x < 50', 'x < 60', 'x < 70', 'x < 80'],
    'longs_1h_chg%': ['x > 1', 'x > 2', 'x > 3', 'x > 5', 'x < -1', 'x < -2', 'x < -3', 'x < -5'],
    'longs_24h_chg%': ['x > 1', 'x > 2', 'x > 3', 'x > 5', 'x < -1', 'x < -2', 'x < -3', 'x < -5'],
    'oi_1h_chg%': ['x > 1', 'x > 2', 'x > 3', 'x > 5', 'x < -1', 'x < -2', 'x < -3', 'x < -5'],
    'oi_24h_chg%': ['x > 1', 'x > 2', 'x > 3', 'x > 5', 'x < -1', 'x < -2', 'x < -3', 'x < -5'],
    'breakout_24h': ['x == True'],
    'breakout_7d': ['x == True'],
    'breakout_14d': ['x == True'],
    'breakout_30d': ['x == True'],
    'n_hours_breakout': ['x > 168', 'x > 336', 'x > 720', 'x > 1440', 'x > 4320']
}

# Transformer le dictionnaire 'conditions' en une liste de tuples (clé, condition)
conditions_list = [(cle, condition) for cle, conditions in conditions.items() for condition in conditions]

# cette fonction génère toutes les combinaisons possibles sans prendre un même clé dans une combinaison
def generer_toutes_combinaisons(conditions_list, taille_combinaison=3):
    # Regrouper les conditions par clé
    conditions_par_cle = {}
    for cle, condition in conditions_list:
        if cle not in conditions_par_cle:
            conditions_par_cle[cle] = []
        conditions_par_cle[cle].append((cle, condition))

    # Générer des combinaisons possibles pour chaque clé
    combinaisons_possibles_par_cle = [conditions for conditions in conditions_par_cle.values()]

    # Générer toutes les combinaisons possibles de clés sans répétition
    combinaisons_de_cles = list(combinations(conditions_par_cle.keys(), taille_combinaison))

    # Pour chaque combinaison de clés, générer le produit cartésien des conditions
    combinaisons_finales = []
    for combinaison_de_cles in combinaisons_de_cles:
        # Sélectionner les listes de conditions pour chaque clé dans la combinaison actuelle
        listes_de_conditions = [conditions_par_cle[cle] for cle in combinaison_de_cles]
        # Générer le produit cartésien de ces listes de conditions
        for produit in product(*listes_de_conditions):
            combinaisons_finales.append(produit)

    return combinaisons_finales

combinaisons_de_conditions = generer_toutes_combinaisons(conditions_list, 3)
print(f"{len(combinaisons_de_conditions)} COMBINAISONS !")


combinaisons_manuelles2 = [
    (('taker_base_vol',  'x > 2500'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('taker_base_vol',  'x > 2500'), ('h1_chg',  'x > 0.04'), ('breakout_7d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('prev_3h_chg',  'x > 0.04'), ('breakout_7d',  'x == True')),
    (('dollar_volume',  'x > 1000000'), ('h1_chg',  'x > 0.04'), ('breakout_7d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('prev_24h_chg',  'x > 0.07'), ('breakout_7d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('breakout_24h',  'x == True'), ('breakout_7d',  'x == True')),
    (('taker_quote_vol',  'x > 4e7'), ('h1_chg',  'x > 0.04'), ('breakout_7d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('prev_3h_chg',  'x > 0.04'), ('n_day_breakout',  'x > 180')),
    (('dollar_volume',  'x > 1000000'), ('h1_chg',  'x > 0.04'), ('n_day_breakout',  'x > 180')),
    (('taker_base_vol',  'x > 2500'), ('24h_h1_chg_rank',  'x == 2'), ('n_day_breakout',  'x > 180')),
    (('h1_chg',  'x > 0.04'), ('prev_24h_chg',  'x > 0.07'), ('n_day_breakout',  'x > 180')),
    (('h1_chg',  'x > 0.04'), ('breakout_24h',  'x == True'), ('n_day_breakout',  'x > 180')),
    (('h1_chg',  'x > 0.04'), ('breakout_7d',  'x == True'), ('n_day_breakout',  'x > 180')),
    (('prev_3h_chg',  'x > 0.04'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('dollar_volume',  'x > 1000000'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('prev_24h_chg',  'x > 0.07'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('24h_h1_chg_rank',  'x == 2'), ('breakout_24h',  'x == True'), ('breakout_7d',  'x == True')),
    (('taker_base_vol',  'x > 2500'), ('h1_chg',  'x > 0.04'), ('n_day_breakout',  'x > 180')),
    (('dollar_volume',  'x > 1000000'), ('30d_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('30d_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('prev_3h_chg',  'x > 0.04'), ('30d_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('prev_24h_chg',  'x > 0.07'), ('30d_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('30d_h1_chg_rank',  'x == 2'), ('breakout_24h',  'x == True'), ('breakout_7d',  'x == True')),
    (('taker_quote_vol',  'x > 4e7'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('dollar_volume',  'x > 1000000'), ('taker_base_vol',  'x > 2500'), ('breakout_7d',  'x == True')),
    (('taker_base_vol',  'x > 2500'), ('taker_quote_vol',  'x > 4e7'), ('breakout_7d',  'x == True')),
    (('taker_base_vol',  'x > 2500'), ('breakout_24h',  'x == True'), ('breakout_7d',  'x == True')),
    (('taker_quote_vol',  'x > 4e7'), ('30d_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('taker_quote_vol',  'x > 4e7'), ('h1_chg',  'x > 0.04'), ('n_day_breakout',  'x > 180')),
    (('24h_h1_chg_rank',  'x == 2'), ('30d_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True')),
    (('taker_base_vol',  'x > 2500'), ('prev_3h_chg',  'x > 0.04'), ('breakout_7d',  'x == True')),
    (('relative_volume',  'x > 3'), ('taker_base_vol',  'x > 2500'), ('prev_24h_chg',  'x > 0.07')),
    (('relative_volume',  'x > 3'), ('taker_base_vol',  'x > 2500'), ('prev_3h_chg',  'x > 0.04')),
    (('taker_base_vol',  'x > 2500'), ('prev_24h_chg',  'x > 0.07'), ('breakout_7d',  'x == True')),
    (('prev_3h_chg',  'x > 0.04'), ('24h_h1_chg_rank',  'x == 2'), ('n_day_breakout',  'x > 180')),
    (('dollar_volume',  'x > 1000000'), ('24h_h1_chg_rank',  'x == 2'), ('n_day_breakout',  'x > 180')),
    (('h1_chg',  'x > 0.04'), ('24h_h1_chg_rank',  'x == 2'), ('n_day_breakout',  'x > 180')),
    (('prev_24h_chg',  'x > 0.07'), ('24h_h1_chg_rank',  'x == 2'), ('n_day_breakout',  'x > 180')),
    (('24h_h1_chg_rank',  'x == 2'), ('breakout_24h',  'x == True'), ('n_day_breakout',  'x > 180')),
    (('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True'), ('n_day_breakout',  'x > 180')),
    (('relative_volume',  'x > 3'), ('num_trades',  'x > 150000'), ('prev_24h_chg',  'x > 0.07')),
    (('dollar_volume',  'x > 1000000'), ('h1_chg',  'x > 0.04'), ('breakout_14d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('prev_3h_chg',  'x > 0.04'), ('breakout_14d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('prev_24h_chg',  'x > 0.07'), ('breakout_14d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('breakout_24h',  'x == True'), ('breakout_14d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('breakout_7d',  'x == True'), ('breakout_14d',  'x == True')),
    (('h1_chg',  'x > 0.04'), ('breakout_14d',  'x == True'), ('n_day_breakout',  'x > 180')),
    (('relative_volume',  'x > 3'), ('taker_base_vol',  'x > 2500'), ('24h_h1_chg_rank',  'x == 2')),
    (('relative_volume',  'x > 3'), ('prev_3h_chg',  'x > 0.04'), ('24h_h1_chg_rank',  'x == 2'))
    ]
combinaisons_manuelles = [(('taker_base_vol',  'x > 2500'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True'))]



# ------ CLASS & FUNCTIONS  -----------------------------
start_time = time.time()

df = pd.read_csv('btc_fulldata.csv', index_col=0)
fd = open('./results.csv','a')

class StratTester:
    def __init__(self, conditions):
        self.conditions = conditions
        self.df_trades = pd.DataFrame()

    def check_line(self, ligne):
        try:
            if all(eval(condition.replace('x', str(ligne[colonne]))) for colonne, condition in self.conditions):
                self.df_trades = pd.concat([self.df_trades, pd.DataFrame([ligne])], ignore_index=True)
        except NameError:
            pass  # Ignore les lignes avec des valeurs NaN

    def run_exit_strats(self, entry_strategy, sl_strategy, tp_strategy):
        full_df = df
        full_df['open_position'] = full_df['t'].isin(self.df_trades['t'])
        df_actual_trades = pd.DataFrame(columns=["date", "periods", "win", "pnl"])
        in_trade = False
        index_of_entry = ''

        entry_price = 0
        target_price = 0
        stop_loss = 0

        for index, row in full_df.iterrows():
            if row['open_position'] and not in_trade:
                entry_price = entry_strategy(row)  
                stop_loss = sl_strategy(row)  
                target_price = tp_strategy(row, entry_price, stop_loss)

                in_trade = True
                index_of_entry = index
            elif in_trade and row['low'] < stop_loss:
                loss = (stop_loss - entry_price) / entry_price
                new_row = pd.DataFrame({
                    "date": [index_of_entry],
                    "periods": [pd.to_datetime(index) - pd.to_datetime(index_of_entry)],
                    "win": [0],
                    "pnl": [loss]
                })
                df_actual_trades = pd.concat([df_actual_trades, new_row], ignore_index=True)
                in_trade = False

            elif in_trade and row['high'] > target_price:
                gain = (target_price - entry_price) / entry_price
                new_row = pd.DataFrame({
                    "date": [index_of_entry],
                    "periods": [pd.to_datetime(index) - pd.to_datetime(index_of_entry)],
                    "win": [1],
                    "pnl": [gain]
                })
                df_actual_trades = pd.concat([df_actual_trades, new_row], ignore_index=True)
                in_trade = False
        return df_actual_trades


    def display_results(self, df_actual_trades, entry_strategy, sl_strategy, tp_strategy):
        conditions_str = metrics.replace_commas(str(self.conditions))
        num_trades = len(df_actual_trades)
        total_perf = round(100*df_actual_trades['pnl'].sum(), 2)
        avg_perf = round(total_perf / num_trades, 2) if num_trades > 0 else 0  # Évite la division par zéro
        win_rate = round(df_actual_trades['win'].mean() * 100, 1) if num_trades > 0 else 0

        # Affichage des statistiques en utilisant les données préparées
        print('########################################################')
        print(f"Entry Strategy : {conditions_str}")
        print(f"Exit Strategy : {entry_strategy.__name__},{sl_strategy.__name__},{tp_strategy.__name__}")
        print('------')
        print(f"num trades : {num_trades}")
        print(f"Perf%: {total_perf}")
        print(f"avg perf%: {avg_perf}")
        print(f"win rate %: {win_rate}")

        # entry strat, entry_strategy, sl_strategy, tp_strategy, num trades, perf, avg_perf, win_rate
        new_line = f"{conditions_str},{entry_strategy.__name__},{sl_strategy.__name__},{tp_strategy.__name__},{num_trades},{total_perf},{avg_perf},{win_rate}\n"
        fd.write(str(new_line))


for index, combinaison in enumerate(combinaisons_de_conditions):
    strat_instance = StratTester(combinaison)
    df_temp = df.apply(strat_instance.check_line, axis=1) # mesure les conditions d'entrées
    if not strat_instance.df_trades.empty:
        for entry_strategy, sl_strategy, tp_strategy in product(entry_strategies, sl_strategies, tp_strategies):
            df_actual_trades = strat_instance.run_exit_strats(entry_strategy, sl_strategy, tp_strategy)
            strat_instance.display_results(df_actual_trades, entry_strategy, sl_strategy, tp_strategy)

fd.close()

print("--- %s secondes ---" % (time.time() - start_time))
