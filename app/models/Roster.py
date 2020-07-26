from app import db

Roster = db.Table('roster',
        db.Column('team_key', db.String(20), db.ForeignKey('team.team_key')),
        db.Column('player_key', db.String(30), db.ForeignKey('player.player_key')))
