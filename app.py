from flask import Flask, jsonify, render_template, request, send_from_directory, url_for, redirect, session
import sqlite3
from datetime import datetime
from geopy.geocoders import Nominatim

app = Flask(__name__)

app.secret_key = 'super secret key'

def login_user(username, password):
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()  # Ottieni la prima riga corrispondente
    conn.close()  # Chiudi la connessione al database
    
    if user:
        return True
    return False

def ottieni_coordinate(nome_citta):
    geolocatore = Nominatim(user_agent="nome_applicazione")
    posizione = geolocatore.geocode(nome_citta)
    if posizione:
        latitudine = posizione.latitude
        longitudine = posizione.longitude
        return latitudine, longitudine
    else:
        return None

@app.route('/userPage')
def index():
    if 'user' in session:
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT post.id, users.username, post.text, post.date, pins.lat, pins.lon 
            FROM post
            JOIN users ON post.user_id = users.id
            JOIN pins ON post.pin_id = pins.id
            WHERE users.id = ?
            
            ''', 
            (session['user'][0],)
        )
        posts = cursor.fetchall()
        cursor.execute(
            '''
            SELECT COUNT(*) FROM followers WHERE user_id = ?
            ''', 
            (session['user'][0],)
        )
        n_followers = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return render_template('user_page.html', user=session['user'], posts = posts, n_posts = len(posts), n_followers = n_followers)
    else:
        return render_template('register.html')


@app.route('/')
@app.route('/loginPage')
def login_page():
    return render_template('login.html')


@app.route('/registerPage')
def register_page():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    description = request.form['description']
    current_date = datetime.now().date()  # Ottieni solo la data attuale
    
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, description, creation_date) VALUES (?, ?, ?, ?)', (username, password, description, current_date))
    conn.commit()
    conn.close()
    
    return redirect(url_for('login_page'))
    
    
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if login_user(username, password):
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        session['user'] = user
        return redirect(url_for('index'))
    else:
        return 'Invalid username/password'
   
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/user/<int:user_id>/')
def user(user_id):
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM users WHERE id = ?
        ''',
        (user_id,)
    )
    user = cursor.fetchone()
    
    cursor.execute(
        '''
        SELECT post.id, users.username, post.text, post.date, pins.lat, pins.lon 
        FROM post
        JOIN users ON post.user_id = users.id
        JOIN pins ON post.pin_id = pins.id
        WHERE users.id = ?
            
        ''', 
        (user[0],)
    )
    posts = cursor.fetchall()
    cursor.execute(
        '''
            SELECT COUNT(*) FROM followers WHERE user_id = ?
        ''', 
        (user[0],)
    )
    n_followers = cursor.fetchone()[0]
    cursor.execute(
        '''
        SELECT COUNT(*) FROM followers WHERE user_id = ?
        ''',
        (user[0],)
    )
    is_following = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return render_template('other_user_page.html', user = user, posts = posts, n_posts = len(posts), n_followers = n_followers, is_following = is_following)


@app.route('/searchUser', methods=['POST'])
def search_user():
    user_name = request.form['user_name']
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
            SELECT * FROM users WHERE username LIKE ?
        ''',
        ("%" + user_name + "%",)
    )
    users = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('search.html', users = users)
    
    
@app.route('/addFollower/<int:user_id>/', methods=['POST'])
def add_follower(user_id):
    if 'user' in session:  
        user_follower_id = session['user'][0]
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            SELECT COUNT(*) FROM followers WHERE user_id = ? AND follower_id = ?
            ''',
            (user_id, session['user'][0])
        )
        is_following = cursor.fetchone()[0]
        
        if not is_following:
            cursor.execute(
                '''
                INSERT INTO followers (user_id, follower_id) VALUES (?, ?)
                ''',
                (user_id, user_follower_id)
            )
        conn.commit()
        conn.close()
        return redirect(url_for('user', user_id = user_id))
    else:
        return 'Utente non autenticato', 401


@app.route('/removeFollower/<int:user_id>/', methods=['POST'])
def remove_follower(user_id):
    if 'user' in session:
        user_follower_id = session['user'][0]
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            DELETE FROM followers WHERE user_id = ? AND follower_id = ?
            ''',
            (user_id, user_follower_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('user', user_id = user_id))
    else:
        return 'Utente non autenticato', 401


@app.route('/createPost', methods=['POST'])
def add_post():
    if 'user' in session:
        text = request.form['post_text']
        city = request.form['city']
        user_id = session['user'][0]
        current_date = datetime.now().date()
        coordinate = ottieni_coordinate(city)
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            SELECT id FROM pins WHERE lat = ? AND lon = ?
            ''',
            (coordinate[0],coordinate[1])
        )
        
        pin_id = cursor.fetchone()

        
        if not pin_id:
            cursor.execute(
                '''
                INSERT INTO pins (lat, lon) VALUES (?, ?)
                ''',
                (coordinate[0],coordinate[1])
            )
            pin_id = cursor.lastrowid
        else:
            pin_id = pin_id[0]
        cursor.execute(
            '''
            INSERT INTO post (pin_id, user_id, text, date) VALUES (?, ?, ?, ?)
            ''',
            (pin_id, user_id, text, current_date)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return 'Utente non autenticato', 401

if __name__ == '__main__':
    app.run(debug=True)