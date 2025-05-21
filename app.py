from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
from download_pdf import download_pdf_bp
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(download_pdf_bp)

# Load the trained model
with open("fake_review_model.pkl", "rb") as file:
    model = pickle.load(file)

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            review TEXT,
            prediction TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect('/')
        except sqlite3.IntegrityError:
            return "Username already exists"
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        return redirect('/predict')
    else:
        return "Invalid login credentials"

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        review = request.form['review']
        prediction = model.predict([review])[0]
        result = "Real" if prediction == 1 else "Fake"

        # Save to history
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (user_id, review, prediction) VALUES (?, ?, ?)", 
                       (session['user_id'], review, result))
        conn.commit()

        return render_template('index.html', prediction=result)

    return render_template('index.html')

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/')

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT review, prediction FROM history WHERE user_id = ?", (session['user_id'],))
    rows = cursor.fetchall()
    return render_template('history.html', history=rows)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
