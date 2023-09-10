from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('my_app.config')

db = SQLAlchemy(app)


from my_app.routes.auth_routes import auth_routes
from my_app.routes.admin_routes import admin_routes
from my_app.routes.general_routes import general_routes


app.register_blueprint(auth_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(general_routes)
