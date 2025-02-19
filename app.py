from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Expanded list of usernames and passwords
usernames = ['admin', 'user1', 'user2', 'root', 'guest', 'manager', 'supervisor', 'employee', 'staff', 'customer', 'developer', 'tester', 'analyst', 'support', 'helpdesk']
passwords = ['password123', 'qwerty', '123456', 'letmein', 'welcome', 'admin123', 'secret', 'password1', '12345678', 'abc123', 'iloveyou', 'sunshine', 'dragon', 'monkey', 'football']

login_attempts = 0

def create_brute_force_db():
    conn = sqlite3.connect('brute_force_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

def init_brute_force_db():
    conn = sqlite3.connect('brute_force_users.db')
    c = conn.cursor()
    c.execute('DELETE FROM users')
    correct_username = random.choice(usernames)
    correct_password = random.choice(passwords)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (correct_username, correct_password))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('brute_force_users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    valid_user = c.fetchone()
    conn.close()
    return valid_user

@app.route('/', methods=['GET', 'POST'])
def home():
    global login_attempts
    message = ''
    message_class = ''

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        valid_user = authenticate_user(username, password)

        login_attempts += 1

        if valid_user:
            conn_flags = sqlite3.connect('flags.db')
            c_flags = conn_flags.cursor()
            flag_query = "SELECT flag_part FROM flags WHERE flag_type='brute_force'"
            c_flags.execute(flag_query)
            flag = c_flags.fetchone()
            conn_flags.close()
            message = f"Login successful! You've found the correct combination! Flag: {flag[0]}"
            message_class = 'success'
        else:
            message = "Login failed. Try again!"
            message_class = 'danger'

    return render_template('index.html', challenge_type='Brute Force', message=message, message_class=message_class, show_credentials=True, usernames=usernames, passwords=passwords)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = ''
    message_class = ''
    debug = ''
    
    if request.method == 'POST':
        username = request.form.get('username')
        conn_users = sqlite3.connect('brute_force_users.db')
        c_users = conn_users.cursor()
        query = f"SELECT username FROM users WHERE username='{username}'"
        try:
            c_users.execute(query)
            result = c_users.fetchone()
            conn_users.close()
            debug = f"Query: {query}"
            if result:
                message = f"Password reset link sent to user: {result[0]}"
                message_class = 'success'
            else:
                message = "User not found"
                message_class = 'danger'
        except sqlite3.Error as e:
            conn_users.close()
            message = "An error occurred"
            message_class = 'danger'
            debug = f"Error: {str(e)}"
    
    return render_template('index.html', 
                           challenge_type='Forgot Password', 
                           message=message, 
                           message_class=message_class, 
                           debug=debug, 
                           show_credentials=False)

if __name__ == '__main__':
    create_brute_force_db()
    init_brute_force_db()
    app.run(host='0.0.0.0', port=8087, debug=False)
