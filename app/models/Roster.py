from app import db

class Roster(db.Model):
    '''
    ties players to a team
    '''

    __tablename__ = 'roster'

    roster_pk = db.Column('roster_pk', db.Integer, primary_key=True)
    team_key = db.Column('team_key', db.String(20), db.ForeignKey('team.team_key'), index=True)
    player_key = db.Column('player_key', db.String(30), db.ForeignKey('player.player_key'))
    draft_pick = db.Column('draft_pick', db.Integer)
    draft_round = db.Column('draft_round', db.Integer)
    week = db.Column('week', db.Integer)
 
    #stats_pk = db.Column('stats_pk', db.String(20), db.ForeignKey('stats.stats_pk'), index=True)

    def __init__(self, dict_):
        self.week = dict_.pop('week', 0)
        self.draft_pick = dict_.pop('pick', 0)
        self.draft_round = dict_.pop('round', 0)

        self.__dict__.update(dict_)

    def __str__(self):
        return str(vars(self))

    '''
    def __init__(self, dict_):
        self.draft_pick = '0'

        #identify the team_key
        team = dict_['fantasy_content']['team']
        for entry in team[0]:
            if 'team_key' in entry:
                self.team_key = entry['team_key']

        #identify the player keys
        players = team[1]['roster']['0']['players']
        for entry in players:
            if entry == 'count':
                continue
            for player_dict in players[entry]['player'][0]:
                if 'player_key' in player_dict:
                    self.player_key = player_dict['player_key']

    '''
