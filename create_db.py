import sqlite3
# Connessione al database
conn = sqlite3.connect('./static/data/cityPin.db')
cursor = conn.cursor()

cursor.execute('''
               DELETE FROM post_images
               ''')
conn.commit()
# Chiude la connessione
conn.close()
