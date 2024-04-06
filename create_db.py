import sqlite3
import bcrypt

def hash_password(password):
    # Genera un salt (sale) casuale
    salt = bcrypt.gensalt()
    # Hasha la password con il sale
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Connessione al database
conn = sqlite3.connect('./static/data/cityPin.db')
cursor = conn.cursor()

# Crea una nuova tabella con la struttura desiderata

# Seleziona tutti gli utenti dal database
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

# Per ogni utente, hasha la password esistente e inserisci i dati nella nuova tabella
i = 0
for user in users:
    
    if user[1] == 'admin':
        continue
    i += 1
    user_id = i
    username = user[1]
    password = user[5]
    description = user[2]
    creation_date = user[3]
    profile_image = user[4]

    # Inserisci i dati nella nuova tabella
    cursor.execute('''
        INSERT INTO users_new (id, username, password, description, creation_date, profile_image)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, password, description, creation_date, profile_image))

# Elimina la vecchia tabella degli utenti
cursor.execute('DROP TABLE users')

# Rinomina la nuova tabella per chiamarla "users"
cursor.execute('ALTER TABLE users_new RENAME TO users')

# Committa le modifiche al database
conn.commit()

# Chiude la connessione
conn.close()
