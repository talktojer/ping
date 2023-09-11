import os
import argparse
from my_app import app, db
from my_app.models import User, SystemStatus
from sqlalchemy.exc import IntegrityError

# Argument parser setup
parser = argparse.ArgumentParser(description='Run the Flask app.')
parser.add_argument('--setup', action='store_true', help='Set up database.')
args = parser.parse_args()

# Database setup function
def setup_database():
    db_path = "/usr/app/src/db/users.db"  # Adjust this path as needed

    # Delete the existing database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Old database file deleted.")

    # Create a new database
    with app.app_context():
        db.create_all()
        initial_status = SystemStatus(online=False)
        db.session.add(initial_status)
        db.session.commit()

        # Create initial admin account
        admin_user = User(username='admin', password='password', approved=True)
        try:
            db.session.add(admin_user)
            db.session.commit()
            print("Admin account created.")
        except IntegrityError:
            db.session.rollback()
            print("Admin account already exists.")

# Check if setup argument was passed
if args.setup:
    setup_database()

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8092)
