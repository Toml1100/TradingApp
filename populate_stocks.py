import sqlite3

import alpaca_trade_api as tradeapi

connection = sqlite3.connect('/Users/thomas/Documents/Full_Stack_Trading_App/app.db')
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute(""" SELECT symbol, company FROM stock """)

rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]



api = tradeapi.REST('PKC8I2OJYZAI9Q717CI7','290PthaqbcybXKcGaA384FNN8YhbEP3ZpMUuVf3k', base_url='https://paper-api.alpaca.markets')

assets = api.list_assets()

for asset in assets:

    try:
        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
            print(f'added a new stock {asset.symbol} {asset.name}')
            cursor.execute("INSERT INTO stock (symbol, company, exchange) VALUES (?, ?, ?)",(asset.symbol,asset.name,asset.exchange))
    except Exception as e:
        print(asset.symbol)
        print(e)

connection.commit()

print('success')

# stock_prices = cursor.execute(""" SELECT * FROM stock_price """)
# print(stock_prices)
