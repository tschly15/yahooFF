from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = b'hdknbvmsebnapwema/daf864adfa1'
app.port = 5000

login_manager = LoginManager(app)

from app import routes
#app.run(debug=True, ssl_context='adhoc', port=app.port)
