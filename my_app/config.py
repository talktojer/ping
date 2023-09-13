SQLALCHEMY_DATABASE_URI = 'sqlite:////usr/app/src/db/users.db'
SESSION_TYPE = 'filesystem'
SECRET_KEY = 'supersecretkey'
NEW_USERS_APPROVALS = 0
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:////usr/app/src/db/users.db")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")