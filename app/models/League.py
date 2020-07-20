from app import db

class League(db.Model):
    __tablename__ = 'league'

    pk = db.Column(db.Integer, primary_key=True)
    start_week = db.Column(db.Integer) #1
    iris_group_chat_id = db.Column(db.String(10))
    league_key = db.Column(db.String(20), index=True, unique=True) #348.l.222713
    edit_key = db.Column(db.Integer) #16
    allow_add_to_dl_extra_pos = db.Column(db.Integer) #0
    league_type = db.Column(db.String(20)) #private
    renewed = db.Column(db.String(12)) #359_50604
    end_date = db.Column(db.Date)
    is_pro_league = db.Column(db.Integer)
    logo_url = db.Column(db.Boolean)
    start_date = db.Column(db.Date)
    weekly_deadline = db.Column(db.String(10))
    draft_status = db.Column(db.String(20)) #postdraft
    season = db.Column(db.Integer) #2015
    is_cash_league = db.Column(db.Integer) #0
    game_code = db.Column(db.String(5)) #nfl
    num_teams = db.Column(db.Integer) #12
    name = db.Column(db.String(50)) #bearlyworking
    scoring_type = db.Column(db.String(10)) #head
    league_id = db.Column(db.Integer) #222713
    current_week = db.Column(db.Integer) #16
    league_update_timestamp = db.Column(db.Integer) #1452151207
    url = db.Column(db.String) #https://football.fantasysports.yahoo.com/archive/nfl/2015/222713
    renew = db.Column(db.String(20)) #331_1136475
    is_finished = db.Column(db.Integer) #1
    end_week = db.Column(db.Integer) #16

    def __repr__(self):
        return '{0} {1} {2} {3}'.format(self.name, self.game_code, self.season, self.league_key)

    def __init__(self, d):
        p = d['fantasy_content']['league'][0]
        self.__dict__.update(p)
