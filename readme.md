# Crypto framework

## Definition
**Variable**: a parameter within a strategy (e.g. day of the week, daily dollar volume, 1-hour-change % etc.) => the full list is given below

**Modality**: a specific filter applied to a variable. For example: day of the week = Monday; daily dollar volume > 1b USD; 1-hour-change % > 5%

Please note that within code, modalities are called *conditions*. 

## Description
This project aims at simulating as many 3-modality-strategies as possible in order to retrieve the most profitable variables.

**The idea is not to overfit to the best strategy but rather to find the most common variables / modalities amongst the top strategies.**

It is built around **one goal** : making it easy to add new variables and modalities, and test them with existing modalities.

*It's basically a grid search applied to many (sometimes complex) modalities*

## Architecture
### collect 
*This folder aims at preparing data for backtesting by: retrieving, storing data and calculating indicators*

- get_date.py retrieves raw data from coinalyze (liquidations, OI, fundings, longs) and ohlc from binance (tf: 1h, 5m)
- main.py calculates the indicators / modalities (detailed below)
- order_book.py is currently running on GCP and storing snapshops of orderbooks in BigQuery every 5 min for later analysis regarding order book 

### backtest
*This folder provides algorithms that backtest strategies*

- main.py is the main backtesting file: 
  it can either test three specific modalities by applying a filter on variables (e.g. [relative_volume > 2] + [breakout_7d = True] + [h1_chg_rank = High] ) or it can run a (shuffled) grid search on all the modalities (which represents millions of strategies).
  
  it accepts mandatory modalities : modalities that would apply to all the strategies tested, particularly usefull to test one specific condition in different environments
  
  strategies can be tested in R factors or in %
  
  strategies are also based on different TP and SL conditions (detailed below)
  
  results are then stored in a csv with detail of the strategy (entry variables, entry type, sl strat, tp strat) and its results: number of trades taken by the strategy,performance (%), avg_perf (%), win_rate (%) => other metrics are available (see metrics.py)

- knife_graber.py is a backtest of a strategy consisting in "grabing knives" : in other words, placing orders far from the market price every hour in case a big flush happens (and rotate those orders every hour). The goal is to identify what would be the optimal size, timeframe and distance from market price in order to profit from such a strategy. 
  
- display_strats.py takes the best strategies identified by main.py and dislay the trades that would have been taken with it as well as their TP and SL. It lets evaluate visually whether the strategies are overfitted and the result of pure luck or not (for example if SL were very close many times but not triggered or if TP was just touched).

- metrics.py contains multiple metrics for evaluating a strategy : log return, cagr, win rate, max drawdown, max consecutives losses, sharpe, percent return, years past, annualized volatility, sharpe ratio, rolling sharpe ratio, annualized downside deviation, sortino ratio, pure profit score, jensens alpha, jensens alpha v2, drawdown series, max drawdown, max drawdown with metadata, log max drawdown ratio, calmar ratio

  => need some small adjustments to be implemented within main.py

### notebooks
*Jupyter notebooks for data analysis based on the results retrieved in backtesting*


## Variables
### Entry variables 
- dollar_volume: Dollar Volume,
- 7d_dollar_volume_rank: 7-Day Dollar Volume Rank (1),
- 30d_dollar_volume_rank: 30-Day Dollar Volume Rank (1),
- 7d_volume_per_trade_rank: 7-Day Volume per Trade Rank (1),
- 30d_volume_per_trade_rank: 30-Day Volume per Trade Rank (1),
- relative_volume: Relative Volume,
- 30d_volume_rank: 30-Day Volume Rank (1),
- num_trades: Number of Trades,
- taker_base_vol: Taker Base Volume,
- taker_quote_vol: Taker Quote Volume,
- h1_chg: 1-Hour Change,
- prev_3h_chg: Previous 3-Hour Change,
- prev_24h_chg: Previous 24-Hour Change,
- 24h_h1_chg_rank: 24-Hour 1-Hour Change Rank (1),
- 30d_h1_chg_rank: 30-Day 1-Hour Change Rank (1),
- fundings_rank: Fundings Rank (1),
- fundings: Fundings,
- liquidation_longs: Liquidation Longs,
- liquidation_shorts: Liquidation Shorts,
- liquidation_longs_rank: Liquidation Longs Rank (1),
- liquidation_shorts_rank: Liquidation Shorts Rank (1),
- long_%: Long Percentage,
- longs_1h_chg%: 1-Hour Longs Change Percentage,
- longs_24h_chg%: 24-Hour Longs Change Percentage,
- oi_1h_chg%: 1-Hour Open Interest Change Percentage,
- oi_24h_chg%: 24-Hour Open Interest Change Percentage,
- breakout_24h: made a 24-Hour Breakout (bool),
- breakout_7d: made a 7-Day Breakout,
- breakout_14d: made a 14-Day Breakout,
- breakout_30d: made a 30-Day Breakout,
- n_hours_breakout_high: Number of Hours Breakout (High),
- n_hours_breakout_close: Number of Hours Breakout (Close),
- closed_green: Closed Green,
- mainly_full_green: Candle is mainly green (>80%),
- sigma_previous_period: Previous Period standard deviation,
- sigma: standard deviation,
- duration_above_SMA20_h1: Duration Above SMA 20 (1 Hour),
- duration_above_SMA50_h1: Duration Above SMA 50 (1 Hour),
- duration_above_SMA20_h1: Duration Above SMA 20 (1 Hour),
- duration_above_SMA50_h1: Duration Above SMA 50 (1 Hour),
- duration_above_SMA20_h4: Duration Above SMA 20 (4 Hours),
- duration_above_SMA50_h4: Duration Above SMA 50 (4 Hours),
- duration_above_EMA7_d: Duration Above EMA 7 (Daily),
- duration_above_SMA20_d: Duration Above SMA 20 (Daily),
- duration_above_SMA50_d: Duration Above SMA 50 (Daily)
- week_day : which day of the week
- week_end : is week end (bool)


*(1) Ranks are classifications based on percentiles that categorize indicator values into different levels (e.g., low, medium, high) according to their relative position within a data distribution.*

### Entries
Choose between entering at candle close or on a breakout

### SL conditions
- sl_low: Defines the stop loss based on the previous candle low 
- sl_previous_low: Defines the stop loss based on the low from two candles ago
- sl_half_low: Defines the stop loss based on the average between close and low of the previous candle
- make_sl_x_percent: Generates a stop loss function based on a defined percentage
- make_sl_x_sigma: Generates a stop loss function based on standard deviation

### TP conditions
- make_tp_XR: Generates a take profit function based on SL and a multiple of R
- make_tp_xpercent: Generates a take profit function based on a defined percentage
- make_tp_x_sigma: Generates a take profit function based on a factor of the standard deviation (Bollinger Bands)









There are also some more strategies that have been tested (breakout, knife_graber) which are detailed in the backtest readme. 
