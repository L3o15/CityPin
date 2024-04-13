import sqlite3
# Connessione al database
conn = sqlite3.connect('./static/data/cityPin.db')
cursor = conn.cursor()

cursor.execute('''
               
               ''')
conn.commit()
# Chiude la connessione
conn.close()
