import sqlite3

def get_connection():
    return sqlite3.connect("studygroup.db")

def add_user(name, email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT)")
    cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()
    return True

def validate_user(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()
    conn.close()
    return user

def save_student(user_id, courses, scores, preferred_time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, courses TEXT, scores TEXT, preferred_time TEXT)")
    cur.execute("INSERT INTO students (user_id, courses, scores, preferred_time) VALUES (?, ?, ?, ?)",
                (user_id, courses, scores, preferred_time))
    conn.commit()
    conn.close()
