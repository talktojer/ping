from flask import Blueprint
from flask import flash

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            user.last_active = datetime.utcnow()
            db.session.commit()
            if user.username == 'admin' or user.approved:
                session['logged_in'] = True
                session['username'] = username
                flash('Login successful', 'success')
                return redirect('/')
            else:
                return "Your account is pending approval. <a href='/'>Back to Main Page</a>"
        else:
            return "Invalid credentials, <a href='/login'>try again</a> or <a href='/register'>register</a>. <a href='/'>Back to Main Page</a>"
    return render_template_string(open('login.html').read() + "<a href='/'>Back to Main Page</a>")




@auth_routes.route('/logout', methods=['GET'])
def logout():
    username = session.pop('username', None)
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_logged_in = False
        db.session.commit()    
    username = session.pop('username', None)
    session.pop('logged_in', None)
    if username:
        logged_in_users.discard(username)  # Remove username from set
    return redirect('/')
    
@auth_routes.route('/logout', methods=['GET'])
def logout():
    username = session.pop('username', None)
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_logged_in = False
        db.session.commit()    
    username = session.pop('username', None)
    session.pop('logged_in', None)
    if username:
        logged_in_users.discard(username)  # Remove username from set
    return redirect('/')


@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        # Check the new_users_approvals variable to set the approved attribute
        approved_status = True if new_users_approvals == 0 else False
        new_user = User(username=username, password=password, approved=approved_status)
        try:
            db.session.add(new_user)
            db.session.commit()

            if new_users_approvals == 0:
                # Send a ping after successful registration
                payload = f'{username} just registered!'
                response = requests.post('http://ntfy.jersweb.net/ping-jer', data=payload)
                response.raise_for_status()

            return "Registration successful. Waiting for admin approval. <a href='/'>Back to Main Page</a>" if not approved_status else "Registration successful. <a href='/'>Back to Main Page</a>"
        except IntegrityError:
            db.session.rollback()
            return "Username already exists. <a href='/'>Back to Main Page</a>"

    return render_template_string(open('register.html').read() + "<a href='/'>Back to Main Page</a>")

