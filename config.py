import misc

class Config(object):
    PORT = 5000
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'postgresql://tschleyer:tschleyer@127.0.0.1/testing'
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://terrence:terrence@127.0.0.1/testing'

    SECRET_KEY = misc.SECRET_KEY
    CLIENT_ID = misc.client_id
    CLIENT_SECRET = misc.client_secret
