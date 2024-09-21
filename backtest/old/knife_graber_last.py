#coding: utf-8
#source activate py39

import pandas as pd
import numpy as np

source_data = '../collect/binance_history/ETHUSDT_binance.csv'
df = pd.read_csv(source_data)
df['date'] = pd.to_datetime(df['Time']/1000, unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
df['max_low_chg'] = df['low']/df['open'] -1
df['next_24h_chg'] = ((df['close'].shift(-24) - df['close']) / df['close']) * 100

import random

def generate_combinations(num_combinations, min_size, max_size, min_level, max_level):
    combinations = []
    
    for _ in range(num_combinations):
        current_size = random.randint(min_size, max_size)
        current_list = []
        remaining_prorata = 1.0

        for i in range(current_size - 1):  # Générer un élément de moins pour contrôler la somme des prorata à la fin
            # S'assurer que le prorata généré est > 0 en laissant suffisamment pour les éléments restants
            prorata = round(random.uniform(0.01, remaining_prorata - (0.01 * (current_size - i - 1))), 2)
            remaining_prorata -= prorata
            level = round(random.uniform(min_level, max_level), 2)
            current_list.append({'level': level, 'prorata': prorata})

        # Ajouter le dernier élément avec le prorata restant pour assurer que la somme soit exactement 1
        level = round(random.uniform(min_level, max_level), 2)
        current_list.append({'level': level, 'prorata': round(remaining_prorata, 2)})

        combinations.append(current_list)
    
    return combinations

# Générer 1000 combinaisons respectant les conditions données
generated_combinations = generate_combinations(2000, 3, 10, -0.5, -0.03)

# Affichage des 5 premières combinaisons pour vérification
for i, combination in enumerate(generated_combinations[:5]):
    print(f"Combinaison {i+1}: {combination}")


max_risk = 10000  # Montant que je suis prêt à perdre au maximum
liq_levels = [0.5, 0.45, 0.4, 0.35, 0.3]  # Niveau auquel je suis liquidé


df_trades = pd.DataFrame(columns=["date", "brokie"] + [f"pnl_{level}" for level in liq_levels] + [f"n_sl_{level}" for level in liq_levels])
df_results = pd.DataFrame(columns=["combination", "exit_condition", "pnl", "n_sl", "n_trades"] + [f"n_sl_{level}" for level in liq_levels])

# Définition des conditions de sortie
exit_conditions = [
    {"type": "periods", "value": 1},
    {"type": "periods", "value": 4},
    {"type": "periods", "value": 12},
    {"type": "periods", "value": 24},
    {"type": "price_change_pct", "value": 10},
    {"type": "price_change_pct", "value": 12},
    {"type": "price_change_pct", "value": 15},
    {"type": "price_change_pct", "value": 17}
]

# Itération sur chaque condition de sortie
for exit_condition in exit_conditions:
    df_trades = df_trades.iloc[0:0]  # Réinitialiser df_trades pour chaque condition de sortie

    # Itération sur chaque combinaison de niveaux d'ordre
    for combination in generated_combinations:
        in_trade = 0
        avg_price = 0
        size = 0
        sls = {level: 0 for level in liq_levels}  # SL par niveau de liquidation
        pnl_values = {level: 0 for level in liq_levels}  # PnL par niveau de liquidation
        brokies = {level: 0 for level in liq_levels}  # Compteur de brokies par niveau de liquidation
        entry_date = None

        for index, row in df.iterrows():
            if row['max_low_chg'] < combination[0]['level'] and not in_trade:
                # Calculer un SL pour chaque niveau de liquidation
                sls = {level: row['open'] * (1 - level) for level in liq_levels}
                entry_date = row['date']
                entry_price = row['open']
                for level in combination:
                    if row['max_low_chg'] < level['level']:
                        for liq_level in liq_levels:
                            # Calculer la distance en pourcentage entre le prix d'ouverture et le niveau de liquidation
                            distance_to_liq_level = (row['open'] - sls[liq_level]) / row['open'] * 100
                            # Vérifier si la distance est inférieure à 3%
                            if distance_to_liq_level < 3:
                                print(f"Position non prise car à moins de 3% du niveau de liquidation: {liq_level}, Distance: {distance_to_liq_level:.2f}%")
                                continue  # Sauter cette itération pour éviter de prendre une position trop proche du niveau de liquidation
                            denominator = (row['open'] * (1 + level['level']) - sls[liq_level])
                            if denominator <= 0:
                                print(f"Attention: Dénominateur nul ou négatif pour le calcul de new_position_size. Niveau de liquidation: {liq_level}, Open: {row['open']}, Level: {level['level']}")
                                continue  # Sauter cette itération pour éviter la division par zéro
                            new_position_size = max_risk * level['prorata'] / denominator
                            if in_trade:
                                avg_price = ((avg_price * size) + (row['open'] * (1 + level['level']) * new_position_size)) / (size + new_position_size)
                            else:
                                in_trade = 1
                                avg_price = row['open'] * (1 + level['level'])
                            size += new_position_size
                        
            if in_trade:
                in_trade += 1
                price_change_pct = ((row['close'] - entry_price) / entry_price) * 100
                should_exit = False
                
                # Vérification de la condition de sortie
                if exit_condition["type"] == "periods" and in_trade == exit_condition["value"]:
                    should_exit = True
                elif exit_condition["type"] == "price_change_pct" and price_change_pct >= exit_condition["value"]:
                    should_exit = True
                
                # Vérifier pour chaque niveau de liquidation si le SL est atteint
                for liq_level in liq_levels:
                    if row['low'] < sls[liq_level]:
                        brokies[liq_level] += 1
                        pnl_values[liq_level] = -max_risk  # Exemple simplifié, ajustez selon votre logique de calcul de PnL
                        
                # Logique pour déterminer si on doit sortir du trade
                if should_exit:
                    # Calculer la PnL pour les niveaux de liquidation non atteints
                    for liq_level in liq_levels:
                        if pnl_values[liq_level] == 0:  # Si le SL pour ce niveau n'a pas été atteint
                            pnl_values[liq_level] = (row['close'] - avg_price) * size  # Exemple simplifié

                    # Enregistrer le trade
                    new_row = {"date": entry_date, "brokie": sum(brokies.values())}
                    new_row.update({f"pnl_{level}": pnl_values[level] for level in liq_levels})
                    new_row.update({f"n_sl_{level}": brokies[level] for level in liq_levels})
                    df_trades = pd.concat([df_trades, pd.DataFrame([new_row])], ignore_index=True)

                    # Réinitialiser les variables pour le prochain trade
                    in_trade = 0
                    size = 0
                    avg_price = 0
                    brokies = {level: 0 for level in liq_levels}
                    pnl_values = {level: 0 for level in liq_levels}

        # Enregistrement des résultats avec la condition de sortie
        new_row = pd.DataFrame({
            "combination": [str(combination)],
            "exit_condition": [f"{exit_condition['type']}={exit_condition['value']}"],
            "pnl": [df_trades[[f"pnl_{level}" for level in liq_levels]].sum().sum()],
            **{f"n_sl_{level}": df_trades[f"n_sl_{level}"].sum() for level in liq_levels},
            "n_trades": [df_trades.shape[0]]
        }, index=[0])
        df_results = pd.concat([df_results, new_row], ignore_index=True)

        # Affichage formaté de new_row
        print("Résultat de la combinaison testée avec la condition de sortie spécifiée:")
        print('Condition d\'entrée : ', str(combination))
        print(f"Condition de sortie: {new_row['exit_condition'].values[0]}")
        print(f"PnL total: {new_row['pnl'].values[0]:.2f}")
        for level in liq_levels:
            print(f"Nombre de stop-loss atteints pour le niveau de liquidation {level}: {new_row[f'n_sl_{level}'].values[0]}")
        print(f"Nombre total de trades: {new_row['n_trades'].values[0]}\n")

# Enregistrement des résultats
df_results.to_csv('./data/result_knife.csv', index=False)
