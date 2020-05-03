from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'refresh'

db = SQLAlchemy(app)
migrate = Migrate(app)

from app import routes, models
from app.views import authentication