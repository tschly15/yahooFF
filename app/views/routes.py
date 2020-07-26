import requests
from app import app
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
    params = {'access_token': current_user.user_access_token.strip(), 'format':'json'}

    r = requests.get(yahoo_oauth2.teams_url, params=params)
    if r.status_code == 401:
        abort(401)

    d = r.json()

    teams = []
    p = d['fantasy_content']['users']['0']['user'][1]['teams']
    for tid, team_dct in p.iteritems():
        if tid == 'count':
            continue
        teams.append(Team(team_dct['team']))

    return 'a'+str(len(teams))
    return render_template('teams.html', teams)

    '''
    r = requests.get(yahoo_oauth2.league_url, params=params)
    if r.status_code == 401:
        abort(401)
    print '-'*20,'LEAGUE','-'*20
    print r.json()
    print '-'*50

    l = League(r.json())
    print l

    print '-'*20,'PLAYER','-'*20
    r = requests.get(yahoo_oauth2.player_url, params=params)
    if r.status_code == 401:
        abort(401)
    print r.json()
    print '-'*50

    p = Player(r.json())
    print p
    '''


