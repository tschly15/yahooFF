#!/usr/bin/env python
import json
import requests
from app import app
from app.User import User
from oauthlib.oauth2 import WebApplicationClient
from flask import redirect, request, url_for, session, render_template

#TODO:
#fix yahoo login - there was an issue with my user, so I switched accounts
#put in cpuengineer6 but yahoo listed cpuengineer5
#use dpath
#identify leagues by user, not league id

#QUESTIONS:
#is it better to serialize the user data w/in the session or do a db lookup each time
# -- redis cache?

class league(object):
    '''
    leagues are linked thru 'renew' (previous year, eg.371_84998)
     and 'renewed' (following year, eg.390_137260)
    '''

    base_url = "https://football.fantasysports.yahoo.com/f1"
    v2_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    request_auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
    request_token_url = 'https://api.login.yahoo.com/oauth2/get_token' #doubles as refresh token url

    def __init__(self, league_id):
        self.app_id = "HpucOz7i"
        self.url = "{0}/{1}".format(league.base_url, league_id)

        self.client_secret = "30cbbae3cdf91d86d986bf5c08df5fb9bcf95acb"
        self.client_id = "dj0yJmk9ZkJpU2FlS2c3TWZFJmQ9WVdrOVNIQjFZMDk2TjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTNi"

        self.redirect_url = "https://127.0.0.1:{0}/callback".format(app.port)


@app.route('/')
@app.route('/home', methods=['GET','POST'])
def home():

    if request.method == 'GET':
        for key in session.keys():
            del session[key]
        return render_template('home.html')

    if 'user_id' in request.form:
        user_id = request.form['user_id']
        try:
            #retrieve user data from the database
            session['user'] = User.load_user(user_id).to_json()
        except KeyError:
            #create new user and then serialize w/in session
            session['user'] = User(user_id).to_json()
            return render_template('home.html', session=session, user_id=user_id)
        else:
            return redirect(url_for('leaguer'))

    user = User(load_web_user=session['user'])
    user.league_id = request.form['league_id']
    session['user'] = user.to_json()

    return redirect(url_for('request_auth'))

@app.route('/request_auth', methods=['GET'])
def request_auth():
    '''
    Request an authorization URL
     Send: client_id, redirect_uri, response_type
     Receive: authorization code
    '''

    user = User(load_web_user=session['user'])
    league_obj = league(user.league_id)

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_authorization_request(
            league.request_auth_url,
            redirect_url = league_obj.redirect_url)

    auth_url, headers, body = req
    return redirect(auth_url)

@app.route('/callback', methods=['GET','POST'])
def callback():
    '''
    Exchange authorization code for access token
     Send: client_id, client_secret, redirect_uricode, grant_type
     Receive: access_token, token_type, expire_in, refresh_token, xoauth_yahoo_guid
    '''

    user = User(load_web_user=session['user'])
    league_obj = league(user.league_id)

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_token_request(
            league.request_token_url,
            authorization_response=request.url,
            redirect_url = league_obj.redirect_url,
            client_secret = league_obj.client_secret)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body)

    #store the oauth credentials w/in our user
    user.set_tokens(resp.json())
    user.persist_user()
    session['user'] = user.to_json()

    return redirect(url_for('leaguer'))

@app.route('/refresh', methods=['GET','POST'])
def refresh():
    '''
    Exchange refresh token for a new access token
     Send: client_id, client_secret, redirect_uri, refresh_token, grant_type
     Receive: access_token, token_type, expire_in, refresh_token, xoauth_yahoo_guid
    Note: only the access_token will change (refresh_token does not change)
    '''

    user = User(load_web_user=session['user'])
    league_obj = league(user.league_id)

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_refresh_token_request(
        league.request_token_url,
        refresh_token = user.refresh_token,
        client_id = league_obj.client_id,
        client_secret = league_obj.client_secret,
        redirect_uri = league_obj.redirect_url)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body) 

    #store the oauth credentials w/in our user
    user.set_tokens(resp.json())
    user.persist_user()
    session['user'] = user.to_json()

    return redirect(url_for('leaguer'))

@app.route('/leaguer', methods=['GET','POST'])
def leaguer():

    user = User(load_web_user=session['user'])
    league_obj = league(user.league_id)

    payload = {
        'use_login': '1',
        'format': 'json',
        'access_token': user.access_token,
    }
    players_url = '{0}/league/{1}.l.{2}/players'.format(league.v2_url, '390', user.league_id)

    start = 0
    count_per = 25
    status_code = 200

    while status_code == 200:

        url = '{0};count={1};start={2}'.format(players_url, count_per, start)
        resp = requests.get(url.format(start), params=payload)

        #received an Unauthorized response
        if resp.status_code == 401:
            refresh() #renew our credentials

            user = User(load_web_user=session['user'])
            status_code = 200
            payload['access_token'] = user.access_token
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

