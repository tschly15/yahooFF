import requests
from app import app, db
from app.models.Team import Team 
from app.models.League import League
from app.models.Player import Player
from app.models.Roster import Roster
from app.models.Misc import yahoo_oauth2
from flask import redirect, request, url_for, render_template, abort
from flask_login import current_user, login_required

'''
current_user:
    user_access_token: u'ZdmB36d...'
    user_email: u't@c.com'
    user_expires_in: u'3600'
    user_id: 1
    user_name: u'test_user30'
    user_password_hash: u'pbkdf2:sha256:50000$mz1RU...'
    user_refresh_token: u'ACcmc10dE1GobwnH65atjM4ZG...'
    user_token_type: u'bearer'
    _sa_instance_state: <sqlalchemy.orm.state.InstanceState object at 0x7f29bd087850>
'''

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@login_required
@app.route('/teams', methods=['GET'])
def teams():
    '''retrieve a list of teams this user owns'''

    params = {'format':'json',
            'access_token': current_user.user_access_token.strip()}

    #TODO: don't need to do this every time. create a refresh button to do this
    r = requests.get(yahoo_oauth2.teams_url, params=params)
    if r.status_code == 401:
        abort(401)

    d = r.json()

    teams = []
    p = d['fantasy_content']['users']['0']['user'][1]['teams']
    for tid, team_dct in p.iteritems():
        if tid == 'count':
            continue

        team = Team(team_dct['team'])
        teams.append(team)

        #load the team into the database, if not already there
        if Team.query.filter_by(team_key=team.team_key).first() is None:
            db.session.add(team)
            db.session.commit()

    return render_template('teams.html', teams=teams)

@login_required
@app.route('/team', methods=['GET','POST'])
def team():
    '''
    the team needs to check if the draft results are in the database
    then will check for the weekly rosters
    '''

    team_key = request.form['team_key']
    team = Team.query.filter_by(team_key=team_key).first()

    params = {'format':'json',
            'access_token': current_user.user_access_token.strip()}

    #start querying if we don't at least have draft results
    if Roster.query.filter_by(team_key=roster.team_key).first() is None:

        roster_url = yahoo_oauth2.roster_url.format(team_key)
        r = requests.get(roster_url, params=params)
        if r.status_code == 401:
            abort(401)

        dict_ = r.json()

        #identify the player keys
        players = dict_['fantasy_content']['team'][1]['roster']['0']['players']
        for entry in players:
            if entry == 'count':
                continue
            for player_dict in players[entry]['player'][0]:
                if 'player_key' in player_dict:
                    player_key = player_dict['player_key']
                    roster = Roster(team_key, player_key)

                    #load the roster into the database, if not already there
                    if Roster.query.filter_by(league_key=league.league_key).first() is None:
                        db.session.add(league)
                        db.session.commit()



    print r.json()
    print roster

    #get players from the roster
    #roster = Roster.query.filter_by(team_key=team_key)
    return roster
    #return roster.all()

@login_required
@app.route('/league', methods=['GET','POST'])
def league():
    '''
    use the team key to identify the league_key
    create the League object and store in db
    '''
    team_key = request.form['team_key']
    team = Team.query.filter_by(team_key=team_key).first()

    params = {'format':'json',
            'access_token': current_user.user_access_token.strip()}

    league_key = team_key.rsplit('.',2)[0]
    league_url = yahoo_oauth2.league_url + league_key

    r = requests.get(league_url, params=params)
    if r.status_code == 401:
        abort(401)


    #TODO: incorporate league settings
    league = League(r.json())

    #load the league into the database, if not already there
    if League.query.filter_by(league_key=league.league_key).first() is None:
        db.session.add(league)
        db.session.commit()

    teams_url = yahoo_oauth2.teams_url.format(league_key)
    r = requests.get(teams_url, params=params)
    if r.status_code == 401:
        abort(401)

    d = r.json()
    #retrieve all teams belonging to this league
    teams = []
    p = d['fantasy_content']['league'][1]['teams']
    for tid, team_dct in p.iteritems():
        if tid == 'count':
            continue

        team = Team(team_dct['team'])
        teams.append(team)

        #load the team into the database, if not already there
        if Team.query.filter_by(team_key=team.team_key).first() is None:
            db.session.add(team)
            db.session.commit()

    if False:
        #retrieve all applicable players
        start = 0
        count_per_request = 25
        while True:

            player_url = yahoo_oauth2.player_url.format(
                league_url, start, count_per_request)

            r = requests.get(player_url, params=params)
            if r.status_code == 401:
                abort(401)

            d = r.json()
            players = d['fantasy_content']['league'][1]['players']

            #list of players has been exhausted
            if 'count' not in players or int(players.pop('count')) == 0:
                break
        
            for player_dct in players.values():
                player = Player(player_dct['player'])
                db.session.add(player)
                db.session.commit()

            start += count_per_request

    #now check for the draft and load if available
    #TODO: team must be loaded before the draft results
    if True: #if draft does not exist
        league_draft_url = yahoo_oauth2.league_draft_url.format(league_key)
        r = requests.get(league_draft_url, params=params)
        if r.status_code == 401:
            abort(401)

        draft_dict = r.json()
        with open('ros','w') as f:
            f.write(str(draft_dict))

        for player_dict in draft_dict['fantasy_content']['league'][1]['draft_results'].values():
            #{'player_key': '390.p.28465', 'team_key': '390.l.137260.t.7', 'round': 14, 'pick': 165}
            if not isinstance(player_dict, dict):
                print 'probably "count"'
                continue
            roster = Roster(player_dict['draft_result'])
            db.session.add(roster)
            db.session.commit()

    #TODO: get from league
    eligible_positions = ('QB','RB','WR')

    players = Player.query.all()
    return render_template('players.html', players=players, eligible_positions=eligible_positions)
