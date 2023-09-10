from flask import Blueprint, request, flash, session, redirect, render_template_string
from datetime import datetime
from my_app.models import User
from my_app import db  # Import db from my_app
from sqlalchemy.exc import IntegrityError
import requests

admin_routes = Blueprint('admin_routes', __name__)


@admin_routes.route('/admin', methods=['GET'])
def admin():
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect('/login')
    pending_users = User.query.filter_by(approved=False).all()
    return render_template_string(open('admin.html').read(), pending_users=pending_users)
    

@admin_routes.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == 'POST':
        username = request.form['username'].lower()
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

@admin_routes.route('/admin/toggle', methods=['GET'])
def toggle_online():
    if not session.get('logged_in'):
        return redirect('/login')
    status = SystemStatus.query.first()
    status.online = not status.online
    db.session.commit()
    return jsonify({"status": "success", "online": status.online}), 200

@admin_routes.route('/admin/approve/<int:user_id>', methods=['GET'])
def approve_user(user_id):
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect('/login')
    user = User.query.get(user_id)
    if user:
        user.approved = True
        db.session.commit()
        return redirect('/admin')
    return "User not found."