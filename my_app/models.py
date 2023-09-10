from my_app import db  # Import db from my_app


# Define models
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