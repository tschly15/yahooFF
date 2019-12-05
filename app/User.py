import _pg
import json
from app import login_manager
from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, user_id=None, load_web_user=None, load_db_user=None):
        if user_id is not None:
            self.user_id = user_id
        elif load_web_user is not None:
            self.from_json(load_web_user)
        elif load_db_user is not None:
            self.__dict__ = load_db_user

    def get_id(self):
        return self.user_id

    def set_tokens(self, dct):
        #access_token
        #token_type
        #expires_in
        #xoauth_yahoo_guid
        #refresh_token
        self.__dict__.update(dct)

    @staticmethod
    def query_user(user_id):
        db = _pg.connect("yahoo", user="terrence", passwd="terrence")
        qry = "select 1 from users where user_id='{0}' limit 1"
        res = db.query(qry.format(user_id)).dictresult()
        db.close()
        return res

    @login_manager.user_loader
    def load_user(user_id):
        '''
        Return a User object for a given user_id
         - create a new user if one does not exist
        @login_manager.user_loader
         - sets the callback for reloading a user from the session.
        '''

        db = _pg.connect("yahoo", user="terrence", passwd="terrence")
        qry = "select * from users where user_id='{0}'"

        try:
            _user = db.query(qry.format(user_id)).dictresult()[0]
        except:
            user = User(user_id=user_id)
            user.persist_user() #may need something else here
            return user
        else:
            return User(load_db_user=_user)
        finally:
            db.close()

    def persist_user(self):
        dct = vars(self) 

        db = _pg.connect("yahoo", user="terrence", passwd="terrence")

        user_exists = self.query_user(self.user_id)
        #TODO: strip fields before loading
        if user_exists:
            action = 'updated'
            flds = [ "{0}='{1}'".format(key, val)
                     for key, val in dct.items() ]
            qry = "update users set {0} where user_id='{1}'"\
                    .format(','.join(flds), dct['user_id'])
        else:
            action = 'inserted'
            qry = "insert into users ({0}) values ({1})"\
                .format(','.join(dct.keys()), "'%s'" % "','".join(map(str,dct.values())))

        try:
            db.query(qry)
        except:
            print("Unable to load {0} into the database".format(self.user_id))
        else:
            print("Successfully {0} {1}".format(action, self.user_id))
        finally:
            db.close()

    def to_json(self, indent=0):
        return json.dumps(vars(self), indent=indent)
    def from_json(self, dct):
        self.__dict__ = json.loads(dct)
    def __str__(self):
        return self.to_json()
