import json

class User(object):

    def __init__(self, user_id=None, load_user=None):
        if user_id is not None:
            self.user_id = user_id
        elif load_user is not None:
            self.from_json(load_user)

    def set_tokens(self, dct):
        self.__dict__.update(dct)
        #access_token
        #token_type
        #expires_in
        #xoauth_yahoo_guid
        #refresh_token

    def persist_user(self):
        with open('backup/users.py','a') as f:
            f.write('{0} = {1}'.format(self.user_id, self.to_json(indent=2)))

    def to_json(self, indent=0):
        return json.dumps(vars(self), indent=indent)
    def from_json(self, dct):
        self.__dict__ = json.loads(dct)
