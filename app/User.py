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

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        db = _pg.connect("yahoo", user="terrence", passwd="terrence")
        qry = "select * from users where user_id='{0}'"

        try:
            _user = db.query(qry.format(user_id)).dictresult()[0]
        except:
            return None
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
            print qry
        else:
            action = 'inserted'
            qry = "insert into users ({0}) values ({1})"\
                .format(','.join(dct.keys()), "'%s'" % "','".join(map(str,dct.values())))
            print qry

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


#testing
if __name__ == '__main__':

    dct = {
            u'expires_in': 3600,
            u'token_type': u'bearer',
            u'league_id': u'137260',
            u'user_id': u'cpuengineer6',
            u'xoauth_yahoo_guid': u'TZXDXM5R66MQIM7FAZ3YR5J55A',
            u'refresh_token': u'ACcmc10dE1GobwnH65atjM4ZGxxa0M9TqaaK_rUEkaE5PuK3BL9K',
            u'access_token': u'OJtdJACc4F5aOdxEbHcZbuUBZprREzI46iCZ2QugP19SVosqSzcNahhNdopoLDxeo1hK2A0WVnsD9T5mZRgpuKYCqGNzzmnrFSMTq0ELz3eqG4OYTDuZ72L7eLbR9MvDhBkq949gSMhXQHtIiQSiX6dotoV2XDex5mrZrOJI4IQuWNCaFLMLkb51e8eZIHOJIeG_7Rc109nnVd5d.h8D7VUxE5IToz38r93M8wH117smrCuuF3L48soPZTq4kBI7M0ABNineB0nl3sx3TDLubuouPUrpKn5pVumf0rsdNuc2RCmWqBc72k8BAMXcCTsJqIhY54R8wsG_4VOj3HvEIgu2YpEIhG68SbJQ.5v_TwrqQCdyZ7aNfnfo05y4r5.Gak3oi5MWWldEaROpptd6wkedE.wi5ay9tolzac7rIpLZOEJcRTOHGECL.G3APhPqkjrbMQoTgzuxsnd_QbN6N32Oqq.aPUFKYIhGphLg3_.o91tdGkddb846zdfM.tjVUAW7iWuWSXdyUra5N4_zZ5alwFn_mhecoJNMrxACXBmhBoFf8UX8MAtPymmVw70drevaH.6X_5.CQYQqYm8QVVzQjy8DnjZby6oVymsCEFblw_stAChz69MRru.yzdHQxTaNoE1zCnLjApdbHOcU5w22mrH2kMqfB7wqoE7DLe9i.UU85vscYZO_8.iJn_nNSl2Ba8.n.IAd.1l0QOxee3SQITcI8NU7cJg.GD2zfd0yRVTj6Oc3K9AgehC1xW6zJZgLfs3ErV7ovJzuu.zXfLw7TKwkR3u6QY3pyIJbjE0S.PPJJsFIO0JO8Wn8VuttMDc_AVGaJrStO2rW4CwJTPv_Tb645qxGhuA2aQbORuZiw.MCuxp_EVa.cyY4_Utd4kyfAmeTAWkYchDlita9fhHuiw9cRbdyWhn_Uz87RdsymtYUSae7QrzGeBaB4cycyk1LsmUkKrLgng6uEyZyItlblwd.G_NgRN.SZa7brH5CkVQ.LAknBKOfx7ei2MCX8QxulZ4kXYbkj73cv93sxtQpKPDUVQkIFRwZEbnlCkVkxVo-',
    }

    u1 = User('ser4')
    u1.set_tokens(dct)
    u1.persist_user()
    exit()

    tokens = {

        'access_token': 'access_token',
        'token_type': 'token_type',
        'expires_in': 'expires_in',
        'xoauth_yahoo_guid': 'xoauth_yahoo_guid',
        'refresh_token': 1,
        'user_pk': '1',
    }
    u1.persist_user()
    u1_str = u1.to_json()

    u2 = User(load_web_user=u1_str)
    u2.token_type = 'updated_token'
    u2.refresh_token=1
    print u2.access_token
    u2.persist_user()
    exit(1)

    user = User('user1')

    tokens = {
        'access_token': 'access_token',
        'token_type': 'token_type',
        'expires_in': 'expires_in',
        'xoauth_yahoo_guid': 'xoauth_yahoo_guid',
        'refresh_token': 'refresh_token',
    }

    user.set_tokens(tokens)
    user.persist_user()
    user.load_user('user1')
