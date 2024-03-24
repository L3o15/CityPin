import sqlite3

conn = sqlite3.connect('./static/data/cityPin.db')
cursor = conn.cursor()


"""
# Creazione della tabella degli utenti
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );
    '''
)

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS pins (
        id INTEGER PRIMARY KEY,
        lat REAL NOT NULL,
        lon REAL NOT NULL
    );
    '''
)



cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS likes (
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (post_id) REFERENCES post(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    '''
)

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS comments (
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        date DATE NOT NULL,
        FOREIGN KEY (post_id) REFERENCES post(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    '''
)


# Inserimento di un utente di esempio
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))

cursor.execute(
'''
CREATE TABLE IF NOT EXISTS followers (
    user_id INTEGER NOT NULL,
    follower_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (follower_id) REFERENCES users(id)
);
'''
)


    
    
"""
cursor.execute(
    '''
        ALTER TABLE users
        ADD COLUMN profile_image BLOB;
    '''
)

# Salvataggio delle modifiche e chiusura della connessione
conn.commit()
conn.close()