import requests
from app import app, db
from app.models.Team import Team 
from app.models.League import League
from app.models.Player import Player
from app.models.Misc import yahoo_oauth2
from flask import redirect, request, url_for, render_template, abort
from flask_login import current_user, login_required

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@login_required
@app.route('/home', methods=['GET'])
def home():
    params = {'format':'json',
            'access_token': current_user.user_access_token.strip()}

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
@app.route('/draft', methods=['GET','POST'])
def draft():
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
    #load the team into the database, if not already there
    if League.query.filter_by(league_key=league.league_key).first() is None:
        db.session.add(league)
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
                player = Player(player_dct['player'][0])
                db.session.add(player)
                db.session.commit()

            start += count

    players = Player.query.all()
    return render_template('players.html', players=players)
