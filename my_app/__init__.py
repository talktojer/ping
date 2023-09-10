from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('my_app.config')

db = SQLAlchemy(app)

from my_app.routes import auth_routes, admin_routes

app.register_blueprint(auth_routes)
app.register_blueprint(admin_routes)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    is_logged_in = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime, nullable=True)

class SystemStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    online = db.Column(db.Boolean, default=False)
SQLALCHEMY_DATABASE_URI = 'sqlite:////usr/app/src/db/users.db'
SESSION_TYPE = 'filesystem'
SECRET_KEY = 'supersecretkey'
NEW_USERS_APPROVALS = 0