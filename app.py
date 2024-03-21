from flask import Flask, jsonify, render_template, request, send_from_directory, url_for, redirect, session
import sqlite3
from datetime import datetime

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


@app.route('/userPage')
def index():
    if 'username' in session:
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM post
            JOIN users ON post.user_id = users.id
            JOIN pins ON post.pin_id = pins.id
            WHERE users.id = ?
            
            ''', 
            (session['user'][0],)
        )
        posts = cursor.fetchall()
        print(posts)
        cursor.execute(
            '''
            SELECT COUNT(*) FROM followers WHERE user_id = ?
            ''', 
            (session['user'][0],)
        )
        n_followers = cursor.fetchone()[0]
        print(n_followers)
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

if __name__ == '__main__':
    app.run(debug=True)