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
