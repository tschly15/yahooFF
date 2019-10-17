import _pg
import json

class User(object):

    def __init__(self, user_id=None, load_web_user=None, load_db_user=None):
        if user_id is not None:
            self.user_id = user_id
        elif load_web_user is not None:
            self.from_json(load_web_user)
        elif load_db_user is not None:
            self.__dict__ = load_db_user

    def set_tokens(self, dct):
        #access_token
        #token_type
        #expires_in
        #xoauth_yahoo_guid
        #refresh_token
        self.__dict__.update(dct)

    @staticmethod
    def get_user(user_id):
        db = _pg.connect("yahoo", user="terrence", passwd="terrence")
        qry = "select * from users where user_id='{0}'"

        try:
            _user = db.query(qry.format(user_id)).dictresult()[0]
        except:
            return "Could not locate user_id {0}".format(user_id)
        else:
            return User(load_db_user=_user)
        finally:
            db.close()

    def persist_user(self):
        dct = vars(self) 

        db = _pg.connect("yahoo", user="terrence", passwd="terrence")
        qry = "insert into users ({0}) values ({1})"

        try:
            db.query(qry.format(','.join(dct.keys()), "'%s'" % "','".join(dct.values())))
        except:
            print("Unable to load {0} into the database".format(self.user_id))
        else:
            print("Successfully loaded {0} into the database".format(self.user_id))
        finally:
            db.close()

    def to_json(self, indent=0):
        return json.dumps(vars(self), indent=indent)
    def from_json(self, dct):
        self.__dict__ = json.loads(dct)
