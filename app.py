#!/usr/bin/env python
import json
import requests
from User import User
from oauthlib.oauth2 import WebApplicationClient
from flask import Flask, redirect, request, url_for, session, render_template

#TODO:
#fix yahoo login - there was an issue with my user, so I switched accounts
#use dpath
#refresh the token
#identify leagues by user, not league id

app = Flask(__name__)
app.secret_key = b'hdknbvmsebnapwema/daf864adfa1'
app.port = 5000

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
            #look up the user in the database
            session['user'] = Users.get_user(user_id).to_json()
        except KeyError:
            user = User(user_id)
            session['user'] = user.to_json()
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

    return redirect(url_for('leaguer'))

#figure out how this will work
@app.route('/refresh', methods=['GET','POST'])
def refresh():
    '''
    Exchange refresh token for a new access token
     Send: client_id, client_secret, redirect_uri, refresh_token, grant_type
     Receive: access_token, token_type, expire_in, refresh_token, xoauth_yahoo_guid
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
    players_url = '{0}/league/{1}.l.{2}/players'.format(v2_url, '390', user.league_id)

    start = 0
    count_per = 25
    status_code = 200

    while status_code == 200:

        url = '{0};count={1};start={2}'.format(players_url, count_per, start)
        resp = requests.get(url.format(start), params=payload)

        #received an Unauthorized response
        if resp.status_code == 401:
            refresh(user.refresh_token)
            user = User(load_web_user=session['user'])
            status_code = 200
            payload['access_token'] = user.access_token
            print 'payload',payload
            print 'user',user
            continue

        print '*'*30, resp.json(),'*'*30
        dct = resp.json()['fantasy_content']
        for key, entry in dct.iteritems():
            print key, entry

        status_code = resp.status_code
        raw_input((start, status_code))
        start += increment

    payload = {
        'format': 'json',
        'access_token': session['access_token'],
    }

    resp = requests.get(url.format('nfl',league_id),
                        params=payload)
    result = resp.json()

    return result

app.run(debug=True, ssl_context='adhoc', port=app.port)


