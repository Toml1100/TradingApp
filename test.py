# i = 0
# for i in range(1,len(symbols),100):

#     r = c.get_price_history(symbols[i],
#         period_type=client.Client.PriceHistory.PeriodType.DAY,
#         period=client.Client.PriceHistory.Period.ONE_DAY,
#         frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE)
#         # frequency=client.Client.PriceHistory.Frequency.MINUTES)
#     assert r.status_code == 200, r.raise_for_status()


#     i = 0
#     symbol_chunks= []

#     for i in range(1,len(symbols),100):
#         symbol_chunk = symbols[i:i+100]
#         symbol_chunks.append(symbol_chunk)

#     print(symbol_chunks)

# for i in range(0,len(symbol_chunks)):
#     for ticker in symbol_chunks[i]:
#         ###### put in request here
#         r = c.get_price_history(symbols[i],
#             period_type=client.Client.PriceHistory.PeriodType.DAY,
#             period=client.Client.PriceHistory.Period.ONE_DAY,
#             frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE)
#             # frequency=client.Client.PriceHistory.Frequency.MINUTES)
#         assert r.status_code == 200, r.raise_for_status()

#         response = r.json()

#         for  bar in response['candles']:


#             date = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(bar['datetime']/1000.))
#             # print(date)

#             # print(f'Open: {bar['open']} Low: {bar['low']} High: {bar['high']} DateTime: {bar['datetime']} Close: {bar['close']} Volume: {bar['volume']}')
#             print(symbols[i], 'Open:' , round(bar['open'],2), 'Low:', bar['low'],'Date:', date)
#     i += 1








#     for i in range(0, len(symbols), chunk_size):
#     symbol_chunk = symbols[i:i+chunk_size]
#     barsets = api.get_barset(symbol_chunk, 'day')
#     for symbol in barsets:
#         print(f"processing symbol {symbol}")
#         for bar in barsets[symbol]:
#             stock_id = stock_dict[symbol]
#             cursor.execute("""
#                 INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))
# connection.commit()







# symbols = []
# stock_dict = {}
# for row in rows:
#     symbol = row['symbol']
#     symbols.append(symbol)
#     stock_dict[symbol] = row['id']