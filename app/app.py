from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# user model - refactor ?
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """
    Home Page router
    """
    if 'user_id' in session:
        # clients = get_clients() implement with integrated FastAPI
        return render_template('home.html', username=session['username']) # , clients=clients)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register User Router
    """
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('users/register.html')
                                                                                                                                    
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Login Router
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('users/home'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('users/login.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    """
    Update user info router
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User details updated successfully.')
        return redirect(url_for('users/home'))
    
    return render_template('users/update.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)