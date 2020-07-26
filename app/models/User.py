from app import db, login_manager

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

#TODO: user_id is not necessary. will load_user/get_user work using user_name?

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, index=True)
    user_email = db.Column(db.String(120), unique=True)
    user_password_hash = db.Column(db.String(128))

    #OAuth tokens
    user_expires_in = db.Column(db.String(50))
    user_token_type = db.Column(db.String(50))
    user_access_token = db.Column(db.VARCHAR)
    user_refresh_token = db.Column(db.String(120))
    
    #leagues = db.relationship(League, secondary=roster, backref=db.backref('roster', lazy='dynamic'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    def get_id(self):
        return self.user_id

    def set_password(self, password):
        self.user_password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.user_password_hash.strip(), password)

    def set_oauth_tokens(self, dct):
        self.user_expires_in = dct['expires_in']
        self.user_token_type = dct['token_type']
        self.user_access_token = dct['access_token']
        self.user_refresh_token = dct['refresh_token']
 
    def __str__(self):
        return "<User {0}>".format(self.user_name)
