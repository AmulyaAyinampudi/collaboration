import os, textwrap

# -----------------------------
# Folder and File Definitions
# -----------------------------
folders = ["templates", "static/css"]
files = {}

# ---------- app.py ----------
files["app.py"] = textwrap.dedent("""\
from flask import Flask, render_template, request, redirect, session
from database import add_user, validate_user, save_student
from matching import compute_matches
from agents import summarize_matches

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if add_user(name, email, password):
            return redirect('/login')
        else:
            return render_template('signup.html', msg="Error creating account. Try again.")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = validate_user(email, password)
        if user:
            session['user'] = {'id': user[0], 'name': user[1]}
            return redirect('/dashboard')
        else:
            return render_template('login.html', msg="Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    msg = ""
    if request.method == 'POST':
        courses = request.form.getlist('course_name[]')
        scores = request.form.getlist('course_score[]')
        preferred_time = request.form['preferred_time']
        course_data = {courses[i]: scores[i] for i in range(len(courses)) if courses[i] and scores[i]}
        save_student(session['user']['id'], str(list(course_data.keys())), str(course_data), preferred_time)
        msg = "Details saved successfully!"

    matches = compute_matches(session['user']['id'])
    recommendation_text = summarize_matches(matches)

    return render_template('dashboard.html', name=session['user']['name'], msg=msg, summary=recommendation_text)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
""")

# ---------- database.py ----------
files["database.py"] = textwrap.dedent("""\
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
""")

# ---------- matching.py ----------
files["matching.py"] = textwrap.dedent("""\
from database import get_connection
import ast

def fetch_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, courses, grades, preferred_times FROM students")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def compute_matches(current_user_id):
    data = fetch_all_students()
    if not data:
        return []

    def to_list(s):
        try: return ast.literal_eval(s)
        except: return []
    def to_dict(s):
        try: return ast.literal_eval(s)
        except: return {}

    users = []
    for uid, c, g, t in data:
        users.append({
            "id": uid,
            "courses": to_list(c),
            "grades": to_dict(g),
            "time": t
        })

    current_user = next((u for u in users if u["id"] == current_user_id), None)
    if not current_user: return []

    matches = []
    for u in users:
        if u["id"] == current_user_id:
            continue
        shared = set(u["courses"]) & set(current_user["courses"])
        if shared and u["time"] == current_user["time"]:
            matches.append({
                "id": u["id"],
                "shared_courses": list(shared),
                "time": u["time"]
            })

    return matches
""")

# ---------- agents.py ----------
files["agents.py"] = textwrap.dedent("""\
def summarize_matches(matches):
    if not matches:
        return "No strong study group matches found yet."

    lines = []
    for m in matches:
        lines.append(f"User {m['id']} shares courses {', '.join(m['shared_courses'])} and prefers {m['time']} sessions.")
    return "\\n".join(lines)
""")

# ---------- templates/signup.html ----------
files["templates/signup.html"] = textwrap.dedent("""\
<!DOCTYPE html>
<html>
<head>
  <title>Sign Up</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
<div class="form-container">
  <h2>Sign Up</h2>
  <form method="POST">
    <input name="name" placeholder="Full Name" required>
    <input type="email" name="email" placeholder="Email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Sign Up</button>
    {% if msg %}<p class="error">{{ msg }}</p>{% endif %}
    <a href="/login">Already have an account?</a>
  </form>
</div>
</body>
</html>
""")

# ---------- templates/login.html ----------
files["templates/login.html"] = textwrap.dedent("""\
<!DOCTYPE html>
<html>
<head>
  <title>Login</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
<div class="form-container">
  <h2>Login</h2>
  <form method="POST">
    <input type="email" name="email" placeholder="Email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Login</button>
    {% if msg %}<p class="error">{{ msg }}</p>{% endif %}
    <a href="/signup">Create an account</a>
  </form>
</div>
</body>
</html>
""")

# ---------- templates/dashboard.html ----------
files["templates/dashboard.html"] = textwrap.dedent("""\
<!DOCTYPE html>
<html>
<head>
  <title>Dashboard</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
<div class="form-container">
  <h2>Welcome, {{ name }}</h2>
  <form method="POST">
    <h3>Enter your course details:</h3>
    <div id="courses-section">
      <div class="course">
        <input name="course_name[]" placeholder="Course Name (e.g., AI)">
        <input name="course_score[]" type="number" placeholder="Marks / CGPA">
      </div>
    </div>
    <button type="button" onclick="addCourse()">+ Add Another Course</button>
    <h3>Select your preferred study timings:</h3>
    <select name="preferred_time">
      <option value="Morning">Morning</option>
      <option value="Evening">Evening</option>
      <option value="Weekend">Weekend</option>
    </select>
    <button type="submit">Save Details</button>
    <p>{{ msg }}</p>
  </form>

  {% if summary %}
  <h3>Recommended Study Matches</h3>
  <p style="text-align:left; white-space:pre-line;">{{ summary }}</p>
  {% endif %}
  
  <a href="/logout">Logout</a>
</div>

<script>
function addCourse() {
  const div = document.createElement("div");
  div.classList.add("course");
  div.innerHTML = `
    <input name="course_name[]" placeholder="Course Name">
    <input name="course_score[]" type="number" placeholder="Marks / CGPA">
  `;
  document.getElementById("courses-section").appendChild(div);
}
</script>
</body>
</html>
""")

# ---------- static/css/style.css ----------
files["static/css/style.css"] = textwrap.dedent("""\
body {
  background-color: #111827;
  color: white;
  font-family: Arial, sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.form-container {
  background: #1f2937;
  padding: 30px;
  border-radius: 10px;
  width: 350px;
  text-align: center;
}
input,button,select {
  width: 100%;
  margin: 10px 0;
  padding: 10px;
  border: none;
  border-radius: 5px;
}
button {
  background-color: #2563eb;
  color: white;
  cursor: pointer;
}
button:hover { background-color: #1d4ed8; }
a { color: #60a5fa; }
.error { color: #f87171; }
""")

# ---------- .env and requirements.txt ----------
files[".env"] = "DB_HOST=localhost\nDB_USER=root\nDB_PASSWORD=your_mysql_password\nDB_NAME=studygroup_ai\n"
files["requirements.txt"] = "Flask\nmysql-connector-python\npython-dotenv\n"

# -----------------------------
# Create folders and files
# -----------------------------
for folder in folders:
    os.makedirs(folder, exist_ok=True)

for path, content in files.items():
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Project created successfully with AI-ready recommendation logic!")
print("\nNext steps:")
print("1️⃣  Create MySQL database and tables (run these in Workbench):")
print("""
CREATE DATABASE studygroup_ai;
USE studygroup_ai;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(120) UNIQUE,
  password VARCHAR(120)
);
CREATE TABLE students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  courses TEXT,
  grades TEXT,
  preferred_times TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
""")
print("2️⃣  Activate venv and install dependencies: pip install -r requirements.txt")
print("3️⃣  Run the app: python app.py")
print("4️⃣  Open in browser: http://127.0.0.1:8080")
