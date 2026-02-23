from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Exam, Question, Result

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(name=name, email=email, password=password, role='student')
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect('/dashboard')
    
    return "Invalid Credentials"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    exams = Exam.query.all()
    return render_template('dashboard.html', exams=exams)

@app.route('/exam/<int:exam_id>', methods=['GET', 'POST'])
def exam(exam_id):
    questions = Question.query.filter_by(exam_id=exam_id).all()
    if request.method == 'POST':
        score = 0
        for q in questions:
            selected = request.form.get(str(q.id))
            if selected == q.correct_option:
                score += 1
        
        result = Result(student_id=session['user_id'], exam_id=exam_id, score=score)
        db.session.add(result)
        db.session.commit()
        return redirect(f'/result/{score}')
    
    return render_template('exam.html', questions=questions)

@app.route('/result/<int:score>')
def result(score):
    return render_template('result.html', score=score)

if __name__ == "__main__":
    app.run(debug=True)
