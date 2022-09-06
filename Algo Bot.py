import os
from turtle import pd
import alpaca_trade_api as tradeapi
import smtplib
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from keras.layers import *
from keras.models import *


def pairs_trading_algo(self):
    # Specify paper trading environment
    os.environ['APCA_API_BASE_URL'] = 'https://paper-api.alpaca.markets'

    # Insert API Credentials
    api = tradeapi.REST('API Key', 'SecretKey', api_version='v2')
    account = api.get_account()

  

    days = 1000
    stock1 = 'ADBE'
    stock2 = 'AAPL'

    # Put Hisrorical Data into variables
    stock1_barset = api.get_bars(stock1, 'day', limit=days)
    stock2_barset = api.get_bars(stock2, 'day', limit=days)
    stock1_bars = stock1_barset[stock1]
    stock2_bars = stock2_barset[stock2]

    # Grab stock1 data and put in to a array
    data_1 = []
    times_1 = []
    for i in range(days):
        stock1_close = stock1_bars[i].c
        stock1_time = stock1_bars[i].t
        data_1.append(stock1_close)
        times_1.append(stock1_time)

    # Grab stock2 data and put in to an array
    data_2 = []
    times_2 = []
    for i in range(days):
        stock2_close = stock2_bars[i].c
        stock2_time = stock1_bars[i].t
        data_2.append(stock2_close)
        times_2.append(stock2_time)

    # Putting them together
    hist_close = pd.DataFrame(data_1, columns=[stock1])
    hist_close[stock2] = data_2

    # Current Spread between the two stocks
    stock1_curr = data_1[days-1]
    stock2_curr = data_2[days-1]
    spread_curr = (stock1_curr-stock2_curr)

    # Moving Average of the two stocks
    move_avg_days = 5

    # Moving averge for stock1
    stock1_last = []
    for i in range(move_avg_days):
        stock1_last.append(data_1[(days-1)-i])

    stock1_hist = pd.DataFrame(stock1_last)

    stock1_mavg = stock1_hist.mean()

    # Moving average for stock2
    stock2_last = []
    for i in range(move_avg_days):
        stock2_last.append(data_2[(days-1)-i])
    stock2_hist = pd.DataFrame(stock2_last)
    stock2_mavg = stock2_hist.mean()

    # Sread_avg
    spread_avg = min(stock1_mavg - stock2_mavg)

    # Spread_factor
    spreadFactor = .01
    wideSpread = spread_avg*(1+spreadFactor)
    thinSpread = spread_avg*(1-spreadFactor)

    # Calc_of_shares_to_trade
    cash = float(account.buying_power)
    limit_stock1 = cash//stock1_curr
    limit_stock2 = cash//stock2_curr
    number_of_shares = int(min(limit_stock1, limit_stock2)/2)

     # Trading_algo
    
    portfolio = api.list_positions()
    clock = api.get_clock()
    
    if clock.is_open == True:
        if bool(portfolio) == False:
            # detect a wide spread
            if spread_curr > wideSpread:
                # short top stock
                api.submit_order(symbol=stock1, qty=number_of_shares, side='sell', type='market', time_in_force='day')

                # Long bottom stock
                api.submit_order(symbol=stock2, qty=number_of_shares, side='buy', type='market', time_in_force='day')
                

            # detect a tight spread
            elif spread_curr < thinSpread:
                # long top stock
                api.submit_order(symbol=stock1, qty=number_of_shares, side='buy', type='market', time_in_force='day')

                # short bottom stock
                api.submit_order(symbol=stock2, qty=number_of_shares, side='sell', type='market', time_in_force='day')
                
        else:
            wideTradeSpread = spread_avg * (1+spreadFactor + .03)
            thinTradeSpread = spread_avg * (1+spreadFactor - .03)
            if spread_curr <= wideTradeSpread and spread_curr >= thinTradeSpread:
                api.close_position(stock1)
                api.close_position(stock2)
   
    return 