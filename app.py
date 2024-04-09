from flask import Flask, jsonify, render_template, request, send_from_directory, url_for, redirect, session
import sqlite3
from datetime import datetime
from geopy.geocoders import Nominatim
import bcrypt
import os 
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'super secret key'

UPLOAD_FOLDER = './static/profile_images/'  # Cartella in cui salvare le immagini
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Estensioni di file consentite

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def hash_password(password):
    # Genera un salt (sale) casuale
    salt = bcrypt.gensalt()
    # Hasha la password con il sale
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def login_user(username, password):
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()

    # Esegui una query per ottenere la password hashata dell'utente dal database
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    hashed_password = cursor.fetchone()

    conn.close()  # Chiudi la connessione al database

    if hashed_password:
        # Se è stata trovata una password hashata nel database, confrontala con la password fornita dall'utente
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password[0]):
            # Se le password corrispondono, restituisci True
            return True

    # Se non viene trovata una corrispondenza dell'utente o se le password non corrispondono, restituisci False
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

def get_user_posts(user_id):
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT post.id, users.username, post.text, post.date, pins.lat, pins.lon, post.arrival_date, post.departure_date 
        FROM post
        JOIN users ON post.user_id = users.id
        JOIN pins ON post.pin_id = pins.id
        WHERE users.id = ?
            
        ''', 
        (user_id,)
    )
    posts = cursor.fetchall()
    ret = []
    for post in posts:
        ret.append(get_post_info(post[0]))
    conn.commit()
    conn.close()
    return ret

def get_post_info(post_id):
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT post.id, users.username, post.text, post.date, pins.lat, pins.lon, post.arrival_date, post.departure_date 
        FROM post
        JOIN users ON post.user_id = users.id
        JOIN pins ON post.pin_id = pins.id
        WHERE post.id = ?
        ''', 
        (post_id,)
    )
    post = cursor.fetchone()
    cursor.execute(
        '''
        SELECT COUNT(*) FROM likes WHERE post_id = ?
        ''',
        (post[0],)
    )
    post += (cursor.fetchone()[0],)
    
    cursor.execute(
        '''
        SELECT COUNT(*) FROM likes WHERE post_id = ? AND user_id = ?
        ''',
        (post[0], session['user'][0])
    )
    
    post += (cursor.fetchone()[0],)
    
    cursor.execute(
        '''
        SELECT users.profile_image FROM users WHERE users.username = ?
        ''',
        (post[1],)
    )
    
    post += (cursor.fetchone()[0],)
    
    cursor.execute(
        '''
        SELECT users.id FROM users WHERE users.username = ?
        ''',
        (post[1],)
    )
    
    post += (cursor.fetchone()[0],)
    
    conn.commit()
    conn.close()
    return post

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/userPage')
def index():
    if 'user' in session:
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        
        posts = get_user_posts(session['user'][0])
        cursor.execute(
            '''
            SELECT COUNT(*) FROM followers WHERE user_id = ?
            ''', 
            (session['user'][0],)
        )
        n_followers = cursor.fetchone()[0]
        profile_image = session['user'][5]
        conn.commit()
        conn.close()
        return render_template('user_page.html', user=session['user'], posts = posts, n_posts = len(posts), n_followers = n_followers, profile_image = profile_image)
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
    hashed_password = hash_password(password)
    description = request.form['description']
    current_date = datetime.now().date()  # Ottieni solo la data attuale
    
    # Controlla se il file è stato fornito nella richiesta
    if 'profile_image' not in request.files:
        return 'File not provided', 400

    profile_image = request.files['profile_image']
    
    # Controlla se il nome del file è valido
    if profile_image and allowed_file(profile_image.filename):
        # Sicuro il nome del file e lo salva nella cartella del progetto
        filename = secure_filename(profile_image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], username + "_profileImg.png")
        profile_image.save(filepath)
        # Costruisci l'URL dell'immagine
        image_url = url_for('static', filename=f'profile_images/{username}_profileImg.png')
    else:
        # Se il file non è valido, restituisci un errore
        return 'Invalid file', 400
    
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    
    # Esegui l'insert nella tabella degli utenti
    cursor.execute('INSERT INTO users (username, password, description, creation_date, profile_image) VALUES (?, ?, ?, ?, ?)', 
                   (username, hashed_password, description, current_date, image_url))
    
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
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM users
        
        '''
    )
    return render_template('search.html', users = cursor.fetchall(), utente = session['user'])


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
    
   
    posts = get_user_posts(user[0])
    cursor.execute(
        '''
            SELECT COUNT(*) FROM followers WHERE user_id = ?
        ''', 
        (user[0],)
    )
    n_followers = cursor.fetchone()[0]
    cursor.execute(
        '''
        SELECT COUNT(*) FROM followers WHERE user_id = ? AND follower_id = ?
        ''',
        (user[0], session['user'][0])
    )
    is_following = cursor.fetchone()[0]
    profile_image = user[5]
    conn.commit()
    conn.close()
    return render_template('other_user_page.html', user = user, posts = posts, n_posts = len(posts), n_followers = n_followers, is_following = is_following, profile_image = profile_image)


@app.route('/userPage/<username>')
def user_page(username):
    print(username)
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT users.id FROM users WHERE username = ?
        ''',
        (username,)
    )
    user_id = cursor.fetchone()[0]
    return redirect(url_for('user', user_id = user_id))


@app.route('/searchUser', methods=['POST'])
def search_user():
    user_name = request.form['user_name']
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
            SELECT * FROM users WHERE username LIKE ? AND users.id != ?
        ''',
        ("%" + user_name + "%", session['user'][0])
    )
    users = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('search.html', users = users, utente = session['user'])
    
    
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
        arrival_date = request.form['arrival_date']
        departure_date = request.form['departure_date']
        print(arrival_date)
        print(departure_date)
        user_id = session['user'][0]
        current_date = datetime.now().date()
        coordinate = ottieni_coordinate(city)
        
        if not coordinate:
            return 'Città non trovata', 404
        
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
            INSERT INTO post (pin_id, user_id, text, date, arrival_date, departure_date) VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (pin_id, user_id, text, current_date, arrival_date, departure_date)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return 'Utente non autenticato', 401


@app.route('/addLike/<int:post_id>/<int:user_id>/<int:h>', methods=['POST'])
def add_like(post_id, user_id, h):
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT COUNT(*) FROM likes WHERE post_id = ? AND user_id = ?
        ''',
        (post_id, session['user'][0])
    )
    is_liked = cursor.fetchone()[0]
    if not is_liked:
        cursor.execute(
            '''
            INSERT INTO likes (post_id, user_id) VALUES (?, ?)
            ''',
            (post_id, session['user'][0])
        )
    conn.commit()
    conn.close()
    if h == 1:
        return redirect(url_for('home'))
    elif h == 2:
        return redirect(url_for('user_page', username = user_id))
    return redirect(url_for('user', user_id = user_id))


@app.route('/removeLike/<int:post_id>/<int:user_id>/<int:h>', methods=['POST'])
def remove_like(post_id, user_id, h):
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        DELETE FROM likes WHERE post_id = ? AND user_id = ?
        ''',
        (post_id, session['user'][0])
    )
    conn.commit()
    conn.close()
    if h == 1:
        return redirect(url_for('home'))
    elif h == 2:
        return redirect(url_for('user_page', username = user_id))
    return redirect(url_for('user', user_id = user_id))


@app.route('/updateAccount', methods=['POST'])
def updateAccount():
    username = request.form['username']
    
    # Verifica se lo username è già presente nel database
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
    existing_user_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Se esiste già un utente con lo stesso username, restituisci un messaggio di errore
    if existing_user_count > 0 and username != session['user'][1]:
        return 'Username already exists', 400
    
    
    description = request.form['description']
    image_url = ""
    
    if 'profile_image' in request.files:
        profile_image = request.files['profile_image']
        
        # Controlla se il nome del file è valido
        if profile_image and allowed_file(profile_image.filename):
            # Sicuro il nome del file e lo salva nella cartella del progetto
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], username + "_profileImg.png")
            profile_image.save(filepath)
            # Costruisci l'URL dell'immagine
            image_url = url_for('static', filename=f'profile_images/{username}_profileImg.png')
        
    id = session['user'][0]
    
    if image_url == "":
        conn = sqlite3.connect('./static/data/cityPin.db')
        cursor = conn.cursor()
        cursor.execute('SELECT profile_image FROM users WHERE id = ?', (id,))
        image_url = cursor.fetchone()[0]
        conn.commit()
        conn.close()
    # Esegui l'aggiornamento nella tabella degli utenti
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET description = ?, profile_image = ?, username = ? WHERE id = ?', 
                   (description, image_url, username, id))
    
    posts = get_user_posts(session['user'][0])
    cursor.execute(
            '''
            SELECT COUNT(*) FROM followers WHERE user_id = ?
            ''', 
        (session['user'][0],)
    )
    n_followers = cursor.fetchone()[0]
    profile_image = session['user'][5]
    session['user'] = cursor.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    conn.commit()
    conn.close()
    
    return redirect(url_for('index', user=session['user'], posts = posts, n_posts = len(posts), n_followers = n_followers, profile_image = profile_image))


@app.route('/home')
def home():
    conn = sqlite3.connect('./static/data/cityPin.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT user_id 
        FROM followers 
        WHERE followers.follower_id = ?
        ''', (session['user'][0],)
    )
    follows_id = cursor.fetchall()
    for i in range(len(follows_id)):
        follows_id[i] = follows_id[i][0]
        
    posts = []
    for id in follows_id:
        posts += get_user_posts(id)
        
    posts = sorted(posts, key=lambda x: x[3], reverse=True)
    
    return render_template('home.html', posts = posts, user = session['user'])


@app.route('/positions', methods=['GET', 'POST'])
def positions():
    if request.method == 'GET':
        return render_template('positions.html', default = True, user = session['user'])
    else:
        username = request.form.get('username')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        city = request.form.get('city')
        pos = []
        
        if username:
            conn = sqlite3.connect('./static/data/cityPin.db')
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM users WHERE username = ?
                ''',
                (username,)
            )
            user = cursor.fetchone()
            if not user:
                return render_template('positions.html', error = 'Utente non trovato', user = session['user'])
            pos = get_user_posts(user[0])
            conn.commit()
            conn.close()
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                pos = [x for x in pos if (x[6] == "" and x[7] == "") or 
                            (x[6] is not None and datetime.strptime(x[6], '%Y-%m-%d') >= start_date_obj and 
                            x[7] is not None and datetime.strptime(x[7], '%Y-%m-%d') <= end_date_obj)]
            if city:
                coord = ottieni_coordinate(city)
                if not coord:
                    return render_template('positions.html', error = 'Città non trovata', user = session['user'])
                pos = [x for x in pos if x[4] == coord[0] and x[5] == coord[1]]
            if not pos:
                return render_template('positions.html', error = 'Nessuna infornazione trovata', user = session['user'])
            return render_template('positions.html', pos = pos, default = False, user = session['user'])
        elif(start_date and end_date):
            conn = sqlite3.connect('./static/data/cityPin.db')
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM post WHERE arrival_date >= ? AND departure_date <= ?
                ''',
                (start_date, end_date)
            )

            positions = cursor.fetchall()
            
            conn.commit()
            conn.close()
            pos = []
            for post in positions:
                pos.append(get_post_info(post[0]))
            
            if city:
                coord = ottieni_coordinate(city)
                if not coord:
                    return render_template('positions.html', error = 'Città non trovata', user = session['user'])
                pos = [x for x in pos if x[4] == coord[0] and x[5] == coord[1]]
            if not pos:
                return render_template('positions.html', error = 'Nessuna infornazione trovata', user = session['user'])
            return render_template('positions.html', pos = pos, default = False, user = session['user'])
        elif city:
            conn = sqlite3.connect('./static/data/cityPin.db')
            cursor = conn.cursor()
            coord = ottieni_coordinate(city)
            if not coord:
                return render_template('positions.html', error = 'Città non trovata', user = session['user'])
            cursor.execute(
                '''
                SELECT * 
                FROM post JOIN pins ON post.pin_id = pins.id
                WHERE lat = ? AND lon = ?
                ''',
                (coord[0], coord[1])
            )
            positions = cursor.fetchall()
            
            conn.commit()
            conn.close()
            pos = []
            for post in positions:
                pos.append(get_post_info(post[0]))
            if not pos:
                return render_template('positions.html', error = 'Nessuna infornazione trovata')
            return render_template('positions.html', pos = pos, default = False, user = session['user'])
            
        return render_template('positions.html', default = True, user = session['user'])

if __name__ == '__main__':
    app.run(debug=True)