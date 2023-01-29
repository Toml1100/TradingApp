import sqlite3
connection = sqlite3.connect('/Users/thomas/Documents/Machine_Learning_First_Attempt/NFL_DATA/NFLData.db')
cursor = connection.cursor()
cursor.execute("""DROP TABLE Matchups""")
cursor.execute("""DROP TABLE defenseRushing""")
connection.commit()