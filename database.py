import mysql.connector, os
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def add_user(name, email, password):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name,email,password))
        conn.commit(); return True
    except mysql.connector.Error as e:
        print("add_user error:", e); return False
    finally:
        cur.close(); conn.close()

def validate_user(email, password):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id,name FROM users WHERE email=%s AND password=%s", (email,password))
    u = cur.fetchone(); cur.close(); conn.close(); return u

def save_student(uid, courses, grades, times):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO students (user_id,courses,grades,preferred_times) VALUES(%s,%s,%s,%s)",
                (uid,courses,grades,times))
    conn.commit(); cur.close(); conn.close()
