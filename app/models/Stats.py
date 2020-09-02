from app import db

class Stats(db.Model):
    __tablename__ = 'stats'

    stats_pk = db.Column(db.String(30), primary_key=True, index=True)
    team_id = db.Column(db.Integer) #9
    team_name = db.Column(db.String(40)) #Thx for the F shack
    team_url = db.Column(db.VARCHAR) #https://football.fantasysports.yahoo.com/f1/11609/9
    team_logo = db.Column(db.VARCHAR) #https://s.yimg.com/cv/apiv2/default/nfl/nfl_1.png
    waiver_priority = db.Column(db.String(4)) #
    number_of_moves = db.Column(db.String(5)) #0
    number_of_trades = db.Column(db.String(5)) #0
    league_scoring_type = db.Column(db.String(20)) #head
    has_draft_grade = db.Column(db.String(5)) #0

    manager1_nickname = db.Column(db.String(30)) #Terrence
    manager1_is_commissioner = db.Column(db.String(1)) #1
    manager1_image_url = db.Column(db.VARCHAR) #https://s.yimg.com/ag/images/default_user_profile_pic_64sq.jpg
    manager1_id = db.Column(db.String(10)) #9
    manager1_email = db.Column(db.String(100)) #cpuengineer5@yahoo.com

    manager2_nickname = db.Column(db.String(30)) #Terrence
    manager2_is_commissioner = db.Column(db.String(1)) #1
    manager2_image_url = db.Column(db.VARCHAR) #https://s.yimg.com/ag/images/default_user_profile_pic_64sq.jpg
    manager2_id = db.Column(db.String(10)) #9
    manager2_email = db.Column(db.String(100)) #cpuengineer5@yahoo.com

    #players = db.relationship(Player, secondary=Roster, backref=db.backref('Roster', lazy='dynamic'))

    def __repr__(self):
        return '{0}, managed by {1}'.format(self.team_name, self.manager1_nickname)

    def __init__(self, team):
        self.team_name = 'default'
        self.manager1_nickname = 'default'
        
        if isinstance(team, dict):
            try:
                self.url = team['url']
            except KeyError:
                return

            self.team_id = team['team_id']
            self.team_name = team['name']
            self.team_key = team['team_key']
            self.team_email = team.get('email_address','')
            self.manager1_nickname = team.get('user_display_name','Gil')

        else:

            for item in team:
                for dct in item:

                    if not dct:
                        continue

                    keys = dct.keys()
                    #NOTE: only for testing
                    if len(keys) > 1:
                        if 'draft_grade' not in keys:
                            print '&'*50, dct
                            continue

                    key = keys[0]

                    if 'draft_grade' in keys:
                        self.draft_grade = dct[key]
                    elif key == 'name':
                        self.team_name = dct[key]
                    elif key == 'team_logos':
                        self.team_logo = dct[key][0]['team_logo']['url']
                    elif key == 'roster_adds':
                        self.roster_adds = dct[key]['value']
                    elif key == 'managers':
                        for idx, mdct in enumerate(dct[key], 1):
                            base = 'manager{0}'.format(idx)
                            manager_dct = {
                                 '{0}_nickname'.format(base): mdct['manager']['nickname'],
                                 '{0}_is_commissioner'.format(base): mdct['manager'].get('is_commissioner','0'),
                                 '{0}_image_url'.format(base): mdct['manager']['image_url'],
                                 '{0}_id'.format(base): mdct['manager']['manager_id'],
                                 '{0}_email'.format(base): mdct['manager'].get('email',''),
                            }
                            self.__dict__.update(manager_dct)
                    else:
                        self.__dict__.update(dct)
