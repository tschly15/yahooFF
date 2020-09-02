from app import db

class Player(db.Model):
    __tablename__ = 'player'

    player_key = db.Column(db.String(20), primary_key=True, index=True) #399.p.5479
    player_id = db.Column(db.Integer) #5479
    name_full = db.Column(db.String(80)) #Drew Brees
    name_first = db.Column(db.String(40)) #Drew
    name_last = db.Column(db.String(50)) #Brees
    name_ascii_first = db.Column(db.String(40)) #Drew
    name_ascii_last = db.Column(db.String(50)) #Brees
    editorial_player_key = db.Column(db.String(30)) #nfl.p.5479
    editorial_team_key = db.Column(db.String(30)) #nfl.t.18
    editorial_team_full_name = db.Column(db.String(30)) #New Orleans Saints
    editorial_team_abbr = db.Column(db.String(10)) #NO
    uniform_number = db.Column(db.String(10)) #6
    display_position = db.Column(db.String(20)) #QB
    position_type = db.Column(db.String(15)) #0
    primary_position = db.Column(db.String(10)) #QB
    bye_week = db.Column(db.String(10)) #6
    average_pick = db.Column(db.Float)

    #League dependent variables
    #is_undroppable = db.Column(db.Integer) #0
    #eligible_position = db.Column(db.String(50)) #QB, Q/W/R/T

    #players = d['fantasy_content']['league'][1]['players']
    #q =       b['fantasy_content']['league'][1]['players']['0']['player'][1]['draft_analysis'][0]['average_pick']
    def __init__(self, p):
        dct = {}

        player, draft = p
        dct['average_pick'] = float(draft['draft_analysis'][0]['average_pick'].strip(' -') or 9999)

        for item in p[0]:

            if not isinstance(item, dict):
                continue

            elif any([ item.get(key)
                for key in ('headshot','eligible_positions','image_url') ]):
                    continue

            elif item.get('name'):
                for name_key, value in item.get('name').iteritems():
                    dct['name_{0}'.format(name_key)] = value

            elif item.get('bye_weeks'):
                dct['bye_week'] = item['bye_weeks']['week']

            else:
                dct.update(item)

        self.__dict__.update(dct)

    def __repr__(self):
        return '{0} {1} {2} {3}'.format(self.name_full, self.player_key, self.editorial_team_abbr, self.display_position)

