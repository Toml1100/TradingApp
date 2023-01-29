import pandas as pd
import time
import requests
current_time = time.time() * 1000

key = 'N7BYGO9JVFTBGNSA2BIASATIG0DBIIIQ@AMER.OAUTHAP'
VERB = 'VERB'
def get_price_history(**kwargs):

    url = f'https://api.tdameritrade.com/v1/marketdata/{VERB}/pricehistory'

    params = {}
    params.update({'apikey': key})

    for arg in kwargs:
        parameter = {arg: kwargs.get(arg)}
        params.update(parameter)

    return requests.get(url, params=params).json()

price_hist = get_price_history(symbol='VERB', periodType='day', frequencyType='minute',startDate=int(current_time)-86400000, endDate= int(current_time))

df_candles = pd.json_normalize(price_hist)
# df_candles = pd.json_normalize(price_hist, record_path=['candles'])

# # Convert to individual Candles records
# df_candles = pd.json_normalize(price_hist, record_path=['candles'])


# df_candles.columns = ['open','high','low','close','volume','datetime']


# # Convert Datetime Format
# df_candles['datetime'] = pd.to_datetime(df_candles['datetime'],unit='ms')


print(df_candles)
