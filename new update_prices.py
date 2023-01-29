import alpaca_trade_api as tradeapi
import sqlite3
import tda
from tda import auth, client
import json
import pandas as pd
import datetime
from datetime import datetime, timedelta
import time
import numpy 
import tulipy as ti


############ TD AMERITRADE PRICE HISTORY REQUEST ###########################
token_path = 'token'
api_key = 'N7BYGO9JVFTBGNSA2BIASATIG0DBIIIQ@AMER.OAUTHAP'
redirect_uri = 'https://localhost'
try:
    c = auth.client_from_token_file(token_path, api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path='/Users/thomas/Documents/TDA API/chromedriver') as driver:
        c = auth.client_from_login_flow(
            driver, api_key, redirect_uri, token_path)

#################-----------------INSERT into database--------------------
connection = sqlite3.connect('/Users/thomas/Documents/Full_Stack_Trading_App/app.db')
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute(""" SELECT symbol, company, id FROM stock """)

rows = cursor.fetchall()
# symbols = [row['symbol'] for row in rows]
symbols = []
stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']

symbol_chunks= []

i=0

for i in range(1,len(symbols),10):
    symbol_chunk = symbols[i:i+10]
    symbol_chunks.append(symbol_chunk)

d = datetime.today() - timedelta(days=1)
yesterday = d.strftime("%Y/%m/%d 05:00:00")
STATUS = 73
tickers = []
i=STATUS
import time
count = STATUS * 10


for i in range(STATUS,len(symbol_chunks)):
    print('----------------------------------')
    print('Displayed', count, 'Price Data Records')
    print('----------------------------------')
    print('Tickers Added:', tickers)
    time.sleep(6)
    for ticker in symbol_chunks[i]:

        tickers.append(ticker)

        r = c.get_price_history(ticker,
            period_type=client.Client.PriceHistory.PeriodType.MONTH,
            period=client.Client.PriceHistory.Period.ONE_MONTH,
            frequency_type=client.Client.PriceHistory.FrequencyType.DAILY)
            # frequency=client.Client.PriceHistory.Frequency.MINUTES)
        assert r.status_code == 200, r.raise_for_status()

        response = r.json()
        # print(type(response))
        recent_closes = []

        # print(response)
        for  bar in response['candles']:

            date = time.strftime('%Y/%m/%d %H:%M:%S',  time.gmtime(bar['datetime']/1000.))           
            recent_closes.append(bar['close'])
            # print(recent_closes)        
            if len(recent_closes) >= 50 and date == yesterday :
                sma_20 = ti.sma(numpy.array(recent_closes), period = 20)[-1]
                sma_50 = ti.sma(numpy.array(recent_closes), period = 50)[-1]
                rsi_14 = ti.rsi(numpy.array(recent_closes), period=14)[-1]
            else:
                sma_20, sma_50, rsi_14 = None, None, None



            stock_id = stock_dict[ticker]
            cursor.execute("""
                INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, adjusted_close, sma_20, sma_50, rsi_14)
                VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?,?)
            """, (stock_id, date, bar['open'], bar['high'], bar['low'], bar['close'], bar['volume'],0, sma_20, sma_50, rsi_14))            
            # print(ticker, bar['close'])

            # print('STOCKDATE', date)
            # print('YESTERDAY', yesterday)


    i += 1
    count += 10
    connection.commit()




