from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = b'hdknbvmsebnapwema/daf864adfa1'
app.port = 5000

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes
