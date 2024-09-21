import pandas as pd
import mplfinance as mpf

# Ce script permet d'afficher les trades des stratégies séléctionnées (df_strategies)

df_strategies = pd.read_csv('./data/best_strats.csv')
df_data = pd.read_csv('./data/btc_fulldata.csv')
df_trades = pd.DataFrame()

# ------------- ENTRIES -------------------------

def entry_close(row):
    return row['close'] 

def entry_breakout(row):
    return row['30d_high'] 


# ------------- STOP LOSSES -------------------------

def sl_low(row):
    return row['low']  

def sl_half_low(row):
    return (row['low']+row['close'])/2

def sl_x_percent(row, x):
    return row['close'] * (1 - x / 100)

def sl_x_sigma(row, x):
    return row['close']-row['sigma']*x



# ------------- TAKE PROFITS -------------------------
def tp_XR(row, x, entry_price=None, stop_loss=None):
    return entry_price + x * (entry_price - stop_loss)

def tp_xpercent(row, x, entry_price=None, stop_loss=None):
    return entry_price*(1+x/100)

def tp_x_sigma(row, x, entry_price=None, stop_loss=None):
    return row['close']+row['sigma']*x


# ------------- MAIN  -------------------------

def plot_trade(df, entry_index, exit_index, win, pnl):
    window = 10
    start = max(0, entry_index - window)
    end = min(len(df), exit_index + window)
    df_trade_window = df.iloc[start:end]

    if not isinstance(df_trade_window.index, pd.DatetimeIndex):
        df_trade_window.index = pd.to_datetime(df_trade_window.index)

    color = '#2ca02c' if win else '#d62728'

    entry_date = df_trade_window.index[entry_index - start]
    exit_date = df_trade_window.index[exit_index - start]

    # Préparer les données pour les points d'entrée et de sortie
    entry_data = pd.Series(index=df_trade_window.index, data=[None]*len(df_trade_window))
    exit_data = pd.Series(index=df_trade_window.index, data=[None]*len(df_trade_window))
    entry_data[entry_date] = df_trade_window['close'][entry_index - start]
    exit_data[exit_date] = df_trade_window['close'][exit_index - start]

    # Créer une série pour la ligne SL ou TP
    if win:  # Si gain, afficher SL
        sl_tp_line = pd.Series(data=stop_loss, index=df_trade_window.index)
    else:  # Si perte, afficher TP
        sl_tp_line = pd.Series(data=target_price, index=df_trade_window.index)

    # Utiliser make_addplot pour ajouter des points d'entrée et de sortie, et la ligne SL/TP
    entry_plot = mpf.make_addplot(entry_data, type='scatter', markersize=200, marker='^', color='green', panel=0, secondary_y=False)
    exit_plot = mpf.make_addplot(exit_data, type='scatter', markersize=200, marker='v', color='red', panel=0, secondary_y=False)
    sl_tp_plot = mpf.make_addplot(sl_tp_line, type='line', width=0.5, color='blue')

    mpf_style = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.size': 8})

    # Tracer le graphique avec les points d'entrée et de sortie, et la ligne SL/TP
    title = f"Trade du {df.iloc[entry_index]['t']} au {df.iloc[exit_index]['t']}: {'Gain' if win else 'Perte'} - PnL: {pnl*100:.2f}%"
    mpf.plot(df_trade_window, type='candle', style=mpf_style, addplot=[entry_plot, exit_plot, sl_tp_plot], volume=True, figratio=(10, 6), title=title)


for index_strat, row_strat in df_strategies.iterrows():
    conditions_str = row_strat['entry_strat'].replace("  ", "), (").replace(": ", ", ").replace("}", ")}").replace("{", "{(").replace("[", "(").replace("]", ")")
    print(conditions_str)
    conditions = eval(conditions_str)
    print('########################################################')
    print(f"Entry Strategy : {conditions}")
    print(f"Exit Strategy : {row_strat['tp_strategy']},{row_strat['sl_strategy']}")

    for _, ligne in df_data.iterrows():
        try:
            if all(eval(condition.replace('x', str(ligne[colonne]))) for colonne, condition in conditions):
                df_trades = pd.concat([df_trades, pd.DataFrame([ligne])], ignore_index=True)
        except NameError:
            pass  # Ignore les lignes avec des valeurs NaN ou des erreurs dans les noms des colonnes

    full_df = df_data
    full_df['open_position'] = full_df['t'].isin(df_trades['t'])
    df_actual_trades = pd.DataFrame(columns=["date", "periods", "win", "pnl"])
    in_trade = False
    index_of_entry = ''

    entry_price = 0
    target_price = 0
    stop_loss = 0

    for index, row in full_df.iterrows():
        if row['open_position'] and not in_trade:
            entry_price = entry_close(row)
            
            # Pour le stop loss
            if row_strat['sl_strategy'] not in ['sl_low', 'sl_previous_low', 'sl_half_low']:
                sl_strategy_info = row_strat['sl_strategy'].rsplit('_', 1)
                sl_strategy_name = sl_strategy_info[0]
                print(sl_strategy_info)
            else:
                sl_strategy_info = []
                sl_strategy_name = row_strat['sl_strategy']

            sl_strategy_var = float(sl_strategy_info[1]) if len(sl_strategy_info) > 1 else None
            sl_strategy_func = globals().get(sl_strategy_name)
            if sl_strategy_func:
                stop_loss = sl_strategy_func(row, sl_strategy_var) if sl_strategy_var is not None else sl_strategy_func(row)
            else:
                print(f"La fonction de stop loss '{sl_strategy_name}' n'est pas définie")
                continue
            
            # Pour le take profit
            tp_strategy_info = row_strat['tp_strategy'].rsplit('_', 1)
            tp_strategy_name = tp_strategy_info[0]
            tp_strategy_var = float(tp_strategy_info[1]) if len(tp_strategy_info) > 1 else None
            
            tp_strategy_func = globals().get(tp_strategy_name)
            if tp_strategy_func:
                target_price = tp_strategy_func(row, tp_strategy_var, entry_price, stop_loss) if tp_strategy_var is not None else tp_strategy_func(row, entry_price, stop_loss)
            else:
                print(f"La fonction de take profit '{tp_strategy_name}' n'est pas définie")
                continue

            in_trade = True
            index_of_entry = index
        elif in_trade and row['low'] < stop_loss:
            loss = -0.01
            new_row = pd.DataFrame({
                "date": [index_of_entry],
                "periods": [index - index_of_entry],
                "win": [0],
                "pnl": [loss]
            })
            df_actual_trades = pd.concat([df_actual_trades, new_row], ignore_index=True)
            in_trade = False
            print(f"Perte - PnL: {loss*100:.2f}%, Durée: {index - index_of_entry} chandeliers")
            plot_trade(full_df, index_of_entry, index, win=False, pnl=loss)
        elif in_trade and row['high'] > target_price:
            gain = 0.01*(target_price - entry_price) / (entry_price - stop_loss)
            new_row = pd.DataFrame({
                "date": [index_of_entry],
                "periods": [index - index_of_entry],
                "win": [1],
                "pnl": [gain]
            })
            df_actual_trades = pd.concat([df_actual_trades, new_row], ignore_index=True)
            in_trade = False
            print(f"Gain - PnL: {gain*100:.2f}%, Durée: {index - index_of_entry} chandeliers")
            plot_trade(full_df, index_of_entry, index, win=True, pnl=gain)

    print(df_actual_trades)
    print('######################## SUMMARY ################################')
    num_trades = len(df_actual_trades)
    total_perf = round(100*df_actual_trades['pnl'].sum(), 2)
    avg_perf = round(total_perf / num_trades, 2) if num_trades > 0 else 0  # Évite la division par zéro
    win_rate = round(df_actual_trades['win'].mean() * 100, 1) if num_trades > 0 else 0
    print(f"Entry Strategy : {conditions}")
    print(f"Exit Strategy : {row_strat['tp_strategy']},{row_strat['sl_strategy']}")
    print('------')
    print(f"num trades : {num_trades}")
    print(f"Perf%: {total_perf}")
    print(f"avg perf%: {avg_perf}")
    print(f"win rate %: {win_rate}")