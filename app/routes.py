#!/usr/bin/env python
import json
import dpath
import requests
from app import app
from app.User import User
from oauthlib.oauth2 import WebApplicationClient
from flask_login import current_user, login_user, login_required
from flask import redirect, request, url_for, session, render_template

#TODO:
#put in cpuengineer6 but yahoo listed cpuengineer5
# --> caching issue? same for windycitylisa

class authentication(object):
    #app_id = "HpucOz7i" #do i need this?

    base_url = "https://football.fantasysports.yahoo.com/f1"
    v2_url = "https://fantasysports.yahooapis.com/fantasy/v2"

    oauth2_base_url = "https://api.login.yahoo.com/oauth2"
    request_auth_url = "{0}/request_auth".format(oauth2_base_url)
    request_token_url = "{0}/get_token".format(oauth2_base_url) #doubles as refresh token url

    client_secret = "30cbbae3cdf91d86d986bf5c08df5fb9bcf95acb"
    client_id = "dj0yJmk9ZkJpU2FlS2c3TWZFJmQ9WVdrOVNIQjFZMDk2TjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTNi"

    redirect_url = "https://127.0.0.1:{0}/callback".format(app.port)

class team_cls(object):
    def __init__(self, x):
        try:
            l1 = x[0] 
        except KeyError:
            l1 = [x]

        #this needs to recursively traverse the json
        for entry in l1:
            if isinstance(entry, dict):
                for k, v in entry.iteritems():
                    setattr(self, k, str(v).strip())

    def get_league_info(self):
        team_key = getattr(self, 'team_key', None)
        if team_key is None:
            return

        #we now have the team key, so get the league information
        url = '{0}/league/{1}'.format(authentication.v2_url, team_key.rsplit('.',2)[0])

        payload = {
            'format': 'json',
            'access_token': current_user.access_token,
        }

        resp = requests.get(url, params=payload)
        resp_dct = resp.json()

        if resp.status_code == 400:
            return resp_dct['error']['description']

        league_dict = resp_dct['fantasy_content']['league'][0]

        league_url = league_dict['url']
        league_name = league_dict['name']
        league_season = league_dict['season']

        print "Welcome to {0} {1}!\nVisit at {2}".format(league_name, league_season, league_url)


    def __str__(self):
        if getattr(self, 'name', None) is None:
            return json.dumps(vars(self), indent=2)
        else:
            return '{0}, {1}'.format(self.name, self.url)

class league(object):
    '''
    leagues are linked thru 'renew' (previous year, eg.371_84998)
     and 'renewed' (following year, eg.390_137260)
    '''

    #data retrieval urls
    manager_leagues = "{0}/users;use_login=1;game_keys=nfl/teams".format(authentication.v2_url)
    manager_current_league = "{0}/users;use_login=1/games;game_keys=nfl/teams".format(authentication.v2_url)

    def __init__(self, league_id):
        self.url = "{0}/{1}".format(authentication.base_url, league_id)


@app.route('/logout', methods=['GET'])
def logout():
    for key in session.keys():
        del session[key]
    return redirect(url_for('login'))

@app.route('/')
@app.route('/login', methods=['GET','POST'])
def login():

    #if current_user.is_authenticated:
        #return redirect(url_for('leaguer'))

    if request.method == 'GET':
        return render_template('login.html')

    user = User(user_id=request.form['user_id'])
    login_user(user)
    current_user.persist_user()

    return redirect(url_for('get_user_leagues'))

@app.route('/request_auth', methods=['GET'])
def request_auth():
    '''
    Request an authorization URL
     Send: client_id, redirect_uri, response_type
     Receive: authorization code
    '''
    client = WebApplicationClient(authentication.client_id)
    req = client.prepare_authorization_request(
            authentication.request_auth_url,
            redirect_url = authentication.redirect_url)

    auth_url, headers, body = req
    return redirect(auth_url)

@app.route('/callback', methods=['GET','POST'])
def callback():
    '''
    Exchange authorization code for access token
     Send: client_id, client_secret, redirect_uricode, grant_type
     Receive: access_token, token_type, expire_in, refresh_token, xoauth_yahoo_guid
    '''
    client = WebApplicationClient(authentication.client_id)
    req = client.prepare_token_request(
            authentication.request_token_url,
            authorization_response=request.url, ##what is this?
            redirect_url = authentication.redirect_url,
            client_secret = authentication.client_secret)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body)

    #permanently store user's oauth credentials
    current_user.set_tokens(resp.json())
    current_user.persist_user()

    return redirect(url_for('get_user_leagues'))

@app.route('/refresh', methods=['GET','POST'])
def refresh():
    '''
    Exchange refresh token for a new access token
     Send: client_id, client_secret, redirect_uri, refresh_token, grant_type
     Receive: access_token, token_type, expire_in, refresh_token, xoauth_yahoo_guid
    Note: only the access_token will change (refresh_token does not change)
    '''
    client = WebApplicationClient(authentication.client_id)
    req = client.prepare_refresh_token_request(
        authentication.request_token_url,
        refresh_token = current_user.refresh_token,
        client_id = authentication.client_id,
        client_secret = authentication.client_secret,
        redirect_uri = authentication.redirect_url)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body) 

    #permanently store user's oauth credentials
    current_user.set_tokens(resp.json())
    current_user.persist_user()

    return redirect(url_for('get_user_leagues'))

@app.route('/get_user_leagues', methods=['GET','POST'])
@login_required
def get_user_leagues():

    payload = {
        'format': 'json',
        'access_token': current_user.access_token,
    }

    #will try to pull out the NFL teams for the logged-in user
    resp = requests.get(league.manager_leagues, params=payload)

    #received an Unauthorized response
    if resp.status_code == 401:

        if not current_user.refresh_token.strip():
            return redirect(url_for('request_auth'))
        else:
            # renew our credentials ...
            refresh() 
            # ... then try one more time
            resp = requests.get(league.manager_leagues, params=payload)

    dct = resp.json()
    teams = dpath.util.get(dct, 'fantasy_content/users/0/user/[1]/teams')
    num_teams = int(teams['count'])

    users_teams = []
    for idx in range(num_teams):
        team = '{0}/team'.format(str(idx))

        team_obj = team_cls(dpath.util.get(teams, team))
        team_obj.get_league_info()
        
        users_teams.append(team_obj)
        
    return ''

@app.route('/leaguer', methods=['GET','POST'])
@login_required
def leaguer():
    league_obj = league(current_user.league_id)

    payload = {
        'format': 'json',
        'access_token': current_user.access_token,
    }

    #will try to pull out the NFL teams for the logged-in user
    resp = requests.get(league_obj.manager_leagues, params=payload)

    #received an Unauthorized response
    if resp.status_code == 401:

        if not current_user.refresh_token.strip():
            return redirect(url_for('request_auth'))
        else:
            refresh() #renew our credentials

            #will try to pull out the NFL teams for the logged-in user
            resp = requests.get(league_obj.manager_leagues, params=payload)

    try:
        with open('output.json','a') as f:
            f.write(json.dumps(resp.json()['fantasy_content'], indent=2))
    except Exception as e:
        print 'failed to create the output file:',e.args
    
    users = resp.json()['fantasy_content']['users']
    for i in range(users['count']):

        games = users[str(i)]['user'][1]['games']
        for j in range(games['count']):

            teams = games[str(j)]['game'][1]['teams']
            for k in range(teams['count']):

                for dct in teams[str(k)]['team'][0]:
                    if 'team_key' in dct:
                        team_key = dct['team_key']


    #we now have the team key, so get the league information
    url = '{0}/league/{1}'.format(authentication.v2_url, team_key.rsplit('.',2)[0])

    resp = requests.get(url, params=payload)
    league_resp = resp.json()['fantasy_content']

    league_url = league_resp['league'][0]['url']
    league_name = league_resp['league'][0]['name']

    return "Welcome to {0}, visit at {1}".format(league_name, league_url)

    '''
    players_url = '{0}/league/{1}.l.{2}/players'.format(league.v2_url, '390', current_user.league_id)
    start = 0
    count_per = 2
    status_code = 200

    while status_code == 200:

        url = '{0};count={1};start={2}'.format(players_url, count_per, start)
        resp = requests.get(url.format(start), params=payload)

        #received an Unauthorized response
        if resp.status_code == 401:

            if not current_user.refresh_token.strip():
                return redirect(url_for('request_auth'))
            else:
                refresh() #renew our credentials

            current_user.set_tokens(resp.json())
            current_user.persist_user()

            status_code = 200
            payload['access_token'] = current_user.access_token
            continue

        dct = resp.json()['fantasy_content']
        for key, entry in dct.iteritems():
            print key, entry

        try:
            with open('output.json','a') as f:
                f.write(json.dumps(dct, indent=2))
        except Exception as e:
            print 'failed to create the output file:',e.args

        status_code = resp.status_code
        raw_input((start, status_code))
        start += count_per
    '''

