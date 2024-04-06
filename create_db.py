import sqlite3
# Connessione al database
conn = sqlite3.connect('./static/data/cityPin.db')
cursor = conn.cursor()

cursor.execute('ALTER TABLE post ADD COLUMN arrival_date DATE')
cursor.execute('ALTER TABLE post ADD COLUMN departure_date DATE')
conn.commit()
# Chiude la connessione
conn.close()
