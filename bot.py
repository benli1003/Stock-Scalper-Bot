import alpaca_trade_api as tradeapi #access alpaca api to do stock orders
import pandas as pd #data manipulation
import talib #technical analysis
import numpy as np #large scale math operations
import time #trade timing
import os #manage api keys
from dotenv import load_dotenv #securely manage api keys


#get protected api keys from .env file and set up api
load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
BASE_URL = os.getenv("BASE_URL")

#connect to API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

SYMBOL = 'NVDA'             # The stock symbol to trade
SCALPING_QUANTITY = 10      # Number of shares per trade
TIMEFRAME = 60              # Scalping interval (60 seconds)
LIMIT = 20                  # Time frame for data processing

#get data and create a spreadsheet
def getData(SYMBOL, LIMIT):
    barset = api.get_barset(SYMBOL, 'minute', LIMIT)
    bars = barset[SYMBOL]
    data = pd.DataFrame({
        'open': [bar.o for bar in bars],
        'high': [bar.h for bar in bars],
        'low': [bar.l for bar in bars],
        'close': [bar.c for bar in bars],
        'volume': [bar.v for bar in bars]
    })
    return data


#calculate SMA(simple moving average) and RSI(relative strength index)
def calculateIndicators(data):
    data['SMA'] = talib.SMA(data['close'], 5) #take closing prices and caluclate 5-period SMA
    data['RSI'] = talib.RSI(data['close'], 14) #take closing prices and calculate 14-period RSI
    return data

#trade signal based on indicators
def tradeSignal(data):
    latestRSI = data['RSI'].iloc[-1]
    latestPrice = data['close'].iloc[-1]
    latestSMA = data['SMA'].iloc[-1]

    #buy: RSI < 30 (oversold) and price is above the SMA (indicates price is starting to rise)
    if latestRSI < 30 and latestPrice > latestSMA:
        return 'BUY'
    
    #sell: RSI > 70 (overbought) and price is below the SMA (indicates prices is starting to decline)
    elif latestRSI > 70 and latestPrice < latestSMA:
        return 'SELL'
    
    #otherwise hold
    return 'HOLD'

#execute trades based on signals
def executeTrade(action):
    if action == 'BUY':
        api.submit_order(SYMBOL, SCALPING_QUANTITY, side='buy', type='market', time_in_force='gtc') #submit buy order
        print(f"Bought {SCALPING_QUANTITY} shares of {SYMBOL}")
    elif action == 'SELL':
        api.submit_order(SYMBOL, SCALPING_QUANTITY, side='sell', type='market', time_in_force='gtc') #submit sell order
        print(f"Sold {SCALPING_QUANTITY} shares of {SYMBOL}")

#scalping loop
while True:
    try:
        data = getData(SYMBOL) #getch date
        data = calculateIndicators(data) #calculate indicators
        action = tradeSignal(data) #determine trade signal
        if action != 'HOLD': #execute trade
            executeTrade(action)
        time.sleep(TIMEFRAME)
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(TIMEFRAME)
