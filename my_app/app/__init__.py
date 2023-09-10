from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('my_app.config')

db = SQLAlchemy(app)

from my_app.routes import auth_routes, admin_routes
app.register_blueprint(auth_routes)
app.register_blueprint(admin_routes)
