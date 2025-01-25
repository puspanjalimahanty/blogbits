from flask import Flask, render_template, request, redirect, url_for, flash, session,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Secret key for session management and flashing messages
app.secret_key = 'your_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# In-memory user storage (for demonstration purposes)
users = []

# Load posts from posts.json
def load_posts():
    try:
        with open('posts.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save posts to posts.json
def save_posts(posts):
    with open('posts.json', 'w') as file:
        json.dump(posts, file)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

# Load user from users list
@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

@app.route('/')
def index():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = {'title': title, 'content': content}

        posts = load_posts()
        posts.append(new_post)
        save_posts(posts)

        return redirect(url_for('index'))

    return render_template('create_post.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        # Check if user already exists
        for user in users:
            if user.email == email:
                flash('Email already registered!', 'danger')
                return redirect(url_for('register'))

        # Register the user
        user_id = len(users) + 1  # A simple way to generate a unique ID
        new_user = User(user_id, username, email, password_hash)
        users.append(new_user)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the email exists and verify password
        for user in users:
            if user.email == email and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/delete/<int:post_id>', methods=['GET'])
@login_required
def delete_post(post_id):
    posts = load_posts()
    if post_id < len(posts):
        del posts[post_id]
        save_posts(posts)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Create the database tables (if they don't exist)
with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            return "User already exists!"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return f"Hello, {username}! You are logged in."
        return "Invalid credentials. Please try again."

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

