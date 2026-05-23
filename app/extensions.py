from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()