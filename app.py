from flask import Flask, request, render_template_string, jsonify, session, redirect, flash
from flask_session import Session
import logging
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import argparse

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/users.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)
Session(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    approved = db.Column(db.Boolean, default=False)

logged_in_users = set()
global_online_status = False

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/admin')
        except IntegrityError:
            db.session.rollback()
            return "Username already exists."

    return render_template_string(open('add_user.html').read())

from flask import flash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.username == 'admin' or user.approved:
                session['logged_in'] = True
                session['username'] = username
                flash('Login successful', 'success')
                return redirect('/')
            else:
                return "Your account is pending approval."
        else:
            return "Invalid credentials, <a href='/login'>try again</a> or <a href='/admin/add_user'>register</a>."
    return render_template_string(open('login.html').read())




@app.route('/logout', methods=['GET'])
def logout():
    username = session.pop('username', None)
    session.pop('logged_in', None)
    if username:
        logged_in_users.discard(username)  # Remove username from set
    return redirect('/')

@app.route('/show_logged_in_users', methods=['GET'])
def show_logged_in_users():
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect('/login')
    return jsonify({"logged_in_users": list(logged_in_users)})


@app.route('/admin/toggle', methods=['GET'])
def toggle_online():
    if not session.get('logged_in'):
        return redirect('/login')
    global global_online_status
    global_online_status = not global_online_status
    return jsonify({"status": "success", "online": global_online_status}), 200

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"online": global_online_status}), 200

@app.route('/', methods=['GET'])
def index():
    logging.info("Inside index")
    return render_template_string(open('index.html').read(), username=session.get('username'))

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect('/login')
    pending_users = User.query.filter_by(approved=False).all()
    return render_template_string(open('admin.html').read(), pending_users=pending_users)


    # Get the logged-in user's username from the session
    username = session.get('username')

    # Check if the username is "admin"
    if username != 'admin':
        return redirect('/')

    logging.info("Inside admin")
    return render_template_string(open('admin.html').read(), username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password, approved=False)
        try:
            db.session.add(new_user)
            db.session.commit()
            return "Registration successful. Waiting for admin approval."
        except IntegrityError:
            db.session.rollback()
            return "Username already exists."
    return render_template_string(open('register.html').read())

@app.route('/admin/approve/<int:user_id>', methods=['GET'])
def approve_user(user_id):
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect('/login')
    user = User.query.get(user_id)
    if user:
        user.approved = True
        db.session.commit()
        return redirect('/admin')
    return "User not found."

@app.route('/ping', methods=['POST'])
def ping():
    logging.info("Inside /ping")
    try:
        data = request.get_json()
        # Use the logged-in username if available, otherwise default to 'Anon Pinger'
        name = session.get('username', data.get('name', 'Anon Pinger'))
        payload = f'Ping! From {name}'
        response = requests.post('http://ntfy.jersweb.net/ping-jer', data=payload)
        response.raise_for_status()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error in /ping: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask app.')
    parser.add_argument('--setup', action='store_true', help='Set up database.')
    args = parser.parse_args()

    if args.setup:
        print("Setting up database...")
        with app.app_context():
            db.create_all()
            
            admin_user = User(username='admin', password='password', approved=True)
            try:
                db.session.add(admin_user)
                db.session.commit()
                print("Admin account created.")
            except IntegrityError:
                db.session.rollback()
                print("Admin account already exists.")
        
        print("Database setup complete.")
        exit(0)
    else:
        app.run(host='0.0.0.0', port=8092)