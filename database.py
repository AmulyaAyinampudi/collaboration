import sqlite3

# ✅ Create or connect to SQLite database file
def get_connection():
    return sqlite3.connect("studygroup.db")


# ✅ Initialize database tables (creates them only if they don’t exist)
def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create students table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            courses TEXT,
            grades TEXT,
            preferred_times TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# ✅ Add new user
def add_user(name, email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Email already exists
        return False
    finally:
        conn.close()


# ✅ Validate user during login
def validate_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()

    conn.close()
    return user


# ✅ Save student course & preference details
def save_student(user_id, courses, grades, preferred_times):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO students (user_id, courses, grades, preferred_times)
        VALUES (?, ?, ?, ?)
    ''', (user_id, courses, grades, preferred_times))

    conn.commit()
    conn.close()
