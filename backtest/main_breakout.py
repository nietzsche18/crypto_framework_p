#coding: utf-8
#source activate py38
# cd desktop/data_analysis/crypto_framework/backtest && activate py38 && python main_breakout.py
# cd desktop/data_analysis/crypto_framework/collect/binance_history && activate py38 && python prepa_history.py

import pandas as pd
import numpy as np
from itertools import combinations, product
from strats import entry_strategies, sl_strategies, tp_strategies
import metrics
import time
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

"""
On a une liste de conditions
On a un GridSearch qui va composer des stratégies sur base de tuple de 3 conditions
On va avoir une classe qui teste ces 3 conditions pour chaque ligne du dataframe 
Pour chaque tuple de 3 conditions, on teste différentes stratégies de sortie (également produites en GridSearch)

Il est possible de changer les conditions manuelles (entrées), puis

"""

# ------ ENTRY CONDITIONS -----------------------------

# Définition des conditions d'entrée dans un trade pour chaque colonne


full_conditions = {
    'dollar_volume': ['x > 100000000'],
    '7d_dollar_volume_rank': ['x == 2', 'x == 1', 'x == 0'],
    '30d_dollar_volume_rank': ['x == 2', 'x == 1', 'x == 0'],
    '7d_volume_per_trade_rank': ['x == 2', 'x == 1', 'x == 0'],
    '30d_volume_per_trade_rank': ['x == 2', 'x == 1', 'x == 0'],
    'relative_volume': ['x > 2', 'x > 3'],
    '30d_volume_rank': ['x == 2', 'x == 1', 'x == 0'],
    'num_trades': ['x > 150000'],
    'taker_base_vol': ['x > 2500'],
    'taker_quote_vol': ['x > 4e7'],
    'h1_chg': ['x > 0', 'x > 1', 'x > 2', 'x > 3', 'x > 4', 'x < 0', 'x < -1', 'x < -2', 'x < -3', 'x < -4'],
    'prev_3h_chg': ['x > 0', 'x > 1', 'x > 2', 'x > 3', 'x > 4', 'x < 0', 'x < -1', 'x < -2', 'x < -3', 'x < -4'],
    'prev_24h_chg': ['x > 0', 'x > 1', 'x > 3', 'x > 5', 'x > 7', 'x < 0', 'x < -1', 'x < -3', 'x < -5', 'x < -7'],
    '24h_h1_chg_rank': ['x == 2'],
    '30d_h1_chg_rank': ['x == 2'],
    'fundings_rank': ['x == 2', 'x == 1', 'x == 0'],
    'fundings': ['x > 0.01', 'x > 0.02', 'x < 0'],
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
    'n_hours_breakout': ['x > 168', 'x > 336', 'x > 720', 'x > 1440', 'x > 4320'],
    'n_hours_breakout_close': ['x > 168', 'x > 336', 'x > 720', 'x > 1440', 'x > 4320']
}


conditions = {
    '7d_dollar_volume_rank': ['x == 2'],
    '7d_volume_per_trade_rank': ['x == 2'],
    'closed_green': ['x == True'],
    'long_%': ['x < 60', 'x < 80'],
    'relative_volume': ['x > 2', 'x > 3', 'x > 4'],
    'week_end': ['x == False'],
}

conditions_obligatoires = { 
    'n_hours_breakout_high': ['x > 168']
}

# Transformer le dictionnaire 'conditions' en une liste de tuples (clé, condition)
conditions_list = [(cle, condition) for cle, conditions in conditions.items() for condition in conditions]

# cette fonction génère toutes les combinaisons possibles sans prendre un même clé dans une combinaison
def generer_toutes_combinaisons(conditions_list, conditions_obligatoires, taille_combinaison=3):
    # Transformer les conditions obligatoires en liste de tuples (clé, condition)
    conditions_obligatoires_list = [(cle, condition) for cle, conditions in conditions_obligatoires.items() for condition in conditions]
    
    # Regrouper les conditions par clé
    conditions_par_cle = {}
    for cle, condition in conditions_list + conditions_obligatoires_list:
        if cle not in conditions_par_cle:
            conditions_par_cle[cle] = []
        conditions_par_cle[cle].append((cle, condition))

    # Générer des combinaisons possibles pour chaque clé
    combinaisons_possibles_par_cle = [conditions for conditions in conditions_par_cle.values()]

    # Générer toutes les combinaisons possibles de clés sans répétition, en incluant au moins une condition obligatoire
    combinaisons_de_cles = list(combinations(conditions_par_cle.keys(), taille_combinaison + 1))  # +1 pour inclure une condition obligatoire

    # Pour chaque combinaison de clés, générer le produit cartésien des conditions
    combinaisons_finales = []
    for combinaison_de_cles in combinaisons_de_cles:
        # Vérifier si la combinaison inclut au moins une clé des conditions obligatoires
        if any(cle in conditions_obligatoires for cle in combinaison_de_cles):
            # Sélectionner les listes de conditions pour chaque clé dans la combinaison actuelle
            listes_de_conditions = [conditions_par_cle[cle] for cle in combinaison_de_cles]
            # Générer le produit cartésien de ces listes de conditions
            for produit in product(*listes_de_conditions):
                combinaisons_finales.append(produit)

    return combinaisons_finales

# Modifier l'appel à la fonction pour inclure les conditions obligatoires
combinaisons_grid_search = generer_toutes_combinaisons(conditions_list, conditions_obligatoires, 3)
random.shuffle(combinaisons_grid_search) # Mélanger aléatoirement combinaisons_grid_search
combinaisons_grid_search = combinaisons_grid_search[:100000]
print(f"{len(combinaisons_grid_search)} COMBINAISONS !")


combinaisons_manuelles = [(('taker_base_vol',  'x > 2500'), ('24h_h1_chg_rank',  'x == 2'), ('breakout_7d',  'x == True'))]

# Pour retester les best_strats (sur un autre dataset)
combinaisons_2 = []
df_strategies = pd.read_csv('./data/best_strats.csv')
for index_strat, row_strat in df_strategies.iterrows():
    conditions_str = row_strat['entry_strat'].replace("  ", "), (").replace(": ", ", ").replace("}", ")}").replace("{", "{(").replace("[", "(").replace("]", ")")
    conditions = eval(conditions_str)
    combinaisons_2.append(conditions)


# CHOISIR ICI :
combinaisons_de_conditions = combinaisons_grid_search
dataset_path = './data/dataset/BTCUSDT_binance2020.csv'
target_path = './data/breakout/results_breakout_2020_v2.csv'
#dataset_path = './data/dataset/btc_fulldata.csv'
starting_date = '2020-01-31 23:00:00'
ending_date = '2024-11-31 23:00:00'
count_in_R = True


# ------ CLASS & FUNCTIONS  -----------------------------
start_time = time.time()

df = pd.read_csv(dataset_path, index_col=0)
#df = pd.read_csv('../collect/binance_history/ETHUSDT_binance_ready.csv', index_col=0)
df.index = pd.to_datetime(df.index)
df = df[df.index > starting_date]
#df = df[df.index < ending_date]


def evaluer_conditions_vectorisees(df, conditions):
    # Initialiser une Series de booléens à True; chaque ligne satisfait toutes les conditions jusqu'à preuve du contraire
    lignes_valides = pd.Series(np.ones(len(df), dtype=bool), index=df.index)
    for colonne, liste_conditions in conditions.items():
        condition_colonne = pd.Series(np.zeros(len(df), dtype=bool), index=df.index)
        for condition in liste_conditions:
            # Construire une chaîne de condition à évaluer
            condition_a_evaluer = condition.replace('x', f"df['{colonne}']")
            # Évaluer la condition et combiner les résultats avec un OR logique
            condition_colonne |= eval(condition_a_evaluer)
        
        # Combinez les résultats de chaque colonne avec un AND logique
        lignes_valides &= condition_colonne
    
    # Filtrer le DataFrame original pour ne garder que les lignes valides
    df_trades = df[lignes_valides]
    
    return df_trades

class StratTester:
    def __init__(self, conditions):
        self.conditions = conditions
        self.df_trades = evaluer_conditions_vectorisees(df, conditions)

    def run_exit_strats(self, entry_strategy, sl_strategy, tp_strategy):
        print('run_exit_strats')
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
                if count_in_R:
                    loss = -0.01
                else :
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
                if count_in_R:
                    gain = 0.01*(target_price - entry_price) / (entry_price - stop_loss)
                else :
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
        print('display_results')
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

        # entry_strat,entry_strategy,sl_strategy,tp_strategy,num_trades,perf,avg_perf,win_rate
        new_line = f"{conditions_str},{entry_strategy.__name__},{sl_strategy.__name__},{tp_strategy.__name__},{num_trades},{total_perf},{avg_perf},{win_rate}\n"
        with open(target_path, 'a') as fd:
            fd.write(str(new_line))


def execute_strategy(combinaison):
    # Transformer le tuple de conditions en dictionnaire
    conditions_dict = {cond[0]: [cond[1]] for cond in combinaison}
    strat_instance = StratTester(conditions_dict)
    if not strat_instance.df_trades.empty and len(strat_instance.df_trades) > 10 :
        results = []
        for entry_strategy, sl_strategy, tp_strategy in product(entry_strategies, sl_strategies, tp_strategies):
            df_actual_trades = strat_instance.run_exit_strats(entry_strategy, sl_strategy, tp_strategy)
            if len(df_actual_trades) > 5:
                strat_instance.display_results(df_actual_trades, entry_strategy, sl_strategy, tp_strategy)

def main():
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(execute_strategy, combinaisons_de_conditions))

if __name__ == '__main__':
    main()
    print("--- %s secondes ---" % (time.time() - start_time))
