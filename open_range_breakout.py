import sqlite3
import alpaca_trade_api as tradeapi
import datetime as date
import tda
from tda import auth, client
import json
import pandas as pd
from datetime import datetime, date
import requests
import pandas as pd
import time
import requests
import smtplib, ssl
current_time = time.time() * 1000

key = 'N7BYGO9JVFTBGNSA2BIASATIG0DBIIIQ@AMER.OAUTHAP'
VERB = 'VERB'
def get_price_history(ticker, **kwargs):

    url = f'https://api.tdameritrade.com/v1/marketdata/{ticker}/pricehistory'

    params = {}
    params.update({'apikey': key})

    for arg in kwargs:
        parameter = {arg: kwargs.get(arg)}
        params.update(parameter)

    return requests.get(url, params=params).json()








######### ALPACA API FOR TRADES ############

api = tradeapi.REST('PKC8I2OJYZAI9Q717CI7','290PthaqbcybXKcGaA384FNN8YhbEP3ZpMUuVf3k', base_url='https://paper-api.alpaca.markets') 



############################################

######### TDA API FOR PRICE DATA ###########

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

############################################

########## DATABASE CONNECTION #############

connection = sqlite3.connect('/Users/thomas/Documents/Full_Stack_Trading_App/app.db')
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id FROM strategy WHERE name = 'opening_range_breakout'
""")

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    SELECT symbol, company
    from stock
    JOIN stock_strategy on stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id = ?
""", (strategy_id,))

######################################################

# Show stocks in database

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]
print(symbols)

messages = []

# current_date = '2021-05-14'
current_date = date.today()
open_bar = f"{current_date} 13:30:00"
end_minute_bar = f"{current_date} 13:45:00"
open_range_breakout_file = open("/Users/thomas/Documents/Full_Stack_Trading_App/opening_range_breakout.txt","a")
orders = api.list_orders(status=all, limit=500, after=f"{current_date}T13:30:00Z")
existing_order_symbols = [order.symbol for order in orders if order.status != 'canceled']
for ticker in symbols:

######## TDA API CALL 1 Minute Bars ###############
    # r = c.get_price_history(ticker,
    #     period_type=client.Client.PriceHistory.PeriodType.DAY,
    #     period=client.Client.PriceHistory.Period.ONE_DAY,
    #     frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE,
    #     frequency=client.Client.PriceHistory.Frequency.EVERY_MINUTE)
    # assert r.status_code == 200, r.raise_for_status()
    # response = r.json()

    response = get_price_history(ticker, symbol=ticker, periodType='day', frequencyType='minute',startDate=int(current_time)-86400000, endDate= int(current_time))
    # response = get_price_history(ticker, symbol=ticker, periodType='day', frequencyType='minute')
    # print(response)
    # Convert to Pandas Dataframe
    df = pd.json_normalize(response)
    # Convert to individual Candles records
    df_candles = pd.json_normalize(response, record_path=['candles'])
    df_candles_2 = pd.json_normalize(response, record_path=['candles'])
    
    df_candles.columns = ['open','high','low','close','volume','datetime']
    df_candles_2.columns = ['open','high','low','close','volume','datetime']

    # Convert Datetime Format
    df_candles['datetime'] = pd.to_datetime(df_candles['datetime'],unit='ms')
    df_candles_2['datetime'] = pd.to_datetime(df_candles_2['datetime'],unit='ms')


    print('********########*********',ticker,'*********###########*************')
    print(df_candles)

    # Drop pre market records from dataframe
    df_candles.drop(df_candles.loc[df_candles['datetime'] < open_bar].index, inplace=True)


    open_bar_low = df_candles.loc[df_candles['datetime'] == open_bar]['low']
    open_bar_high = df_candles.loc[df_candles['datetime'] == open_bar]['high']
    
    # Set 15 minute opening range
    opening_range_mask = (df_candles[df_candles['datetime'] >= open_bar])
    opening_range_mask = (df_candles[df_candles['datetime'] < end_minute_bar]) 

    print(opening_range_mask)

    # Calculate Opening Range
    opening_range_low = opening_range_mask['low'].min()
    opening_range_high = opening_range_mask['high'].max()
    open_bar_range = opening_range_high - opening_range_low

    # Print Opening Range
    print(ticker ,"Open Bar High:", opening_range_high)
    print(ticker ,"Open Bar Low:", opening_range_low)
    print(ticker ,"Open Bar Range:", open_bar_range)

    # After Opening Range
    after_opening_range_bars = (df_candles_2[df_candles_2['datetime'] >= end_minute_bar]) 
    print(after_opening_range_bars)

    # Find Opening Range Breakout
    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]
    print(after_opening_range_breakout)

    port = 465 # SSL
    password = 'weasel4321'

    # Create a secure SSl context
    context = ssl.create_default_context()

    ################# ENTER TRADE HERE #########################
    if not after_opening_range_breakout.empty:
        if ticker not in existing_order_symbols:
            if open_bar_range < 1:
                open_bar_range = 1


            limit_price_1 = after_opening_range_breakout.iloc[0]['close']

            messages.append(f"placing order for {ticker} at {limit_price_1}, closed_above {opening_range_high}\n\n{after_opening_range_breakout.iloc[0]}\n\n")
            open_range_breakout_file.write(f"placing order for {ticker} at {limit_price_1}, closed_above {opening_range_high} at \n{after_opening_range_breakout.iloc[0]}")
            api.submit_order(
                symbol=ticker,
                qty= 20,
                side="buy",
                type= "limit",
                time_in_force= "gtc",
                order_class= "bracket",
                limit_price= limit_price_1,
                take_profit= dict(
                    limit_price= limit_price_1 + open_bar_range,
                    time_in_force= "gtc",
                ),
                stop_loss= dict(
                    stop_price= limit_price_1 - open_bar_range,
                    time_in_force= "gtc",
                )
            )
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login("tom.loudon.5@gmail.com", password)

                email_message = "\n\n".join(messages)

                server.sendmail('tom.loudon.5@gmail.com', 'tom.loudon.5@gmail.com', email_message)        
        else:
            print(f"Already an order for {ticker}, skipping")


print(existing_order_symbols)
print(messages)
#########################################################################
############### Email Sender ############################################
#########################################################################




