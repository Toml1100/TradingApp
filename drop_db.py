import sqlite3
connection = sqlite3.connect('app.db')
cursor = connection.cursor()
cursor.execute("""DROP TABLE stock_price""")
connection.commit()