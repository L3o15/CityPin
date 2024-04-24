import sqlite3

# Connessione al database
conn = sqlite3.connect('./data/cityPin.db')
cursor = conn.cursor()

# Esecuzione della query per ottenere i nomi di tutte le tabelle nel database
cursor.execute("""
                DELETE FROM comments WHERE post_id NOT IN (SELECT id FROM post) OR user_id NOT IN (SELECT id FROM users);
               """)
conn.commit()
conn.close()
