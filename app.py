#!/usr/bin/env python
import json
import requests
from oauthlib.oauth2 import WebApplicationClient
from flask import Flask, redirect, request, url_for, session

#TODO:
#refresh the token
#identify leagues by user, not league id

app = Flask(__name__)
app.secret_key = b'hdknbvmsebnapwema/daf864adfa1'
app.port = 5010

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
def home():
    return '''
    <html>
        <body>
            <form method="get" action="redirector">
                Enter League ID:<br\>
                <input type="text" name="league_id"/>
            </form>
        </body>
    </html>'''

@app.route('/redirector')
def redirector(methods=['GET']):
    session['league_id'] = request.args.get('league_id','137260')
    league_obj = league(session['league_id'])

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_authorization_request(
            league.request_auth_url,
            redirect_url = league_obj.redirect_url)

    auth_url, headers, body = req
    return redirect(auth_url)

@app.route('/callback')
def callback():
    league_obj = league(session['league_id'])

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_token_request(
            league.request_token_url,
            authorization_response=request.url,
            redirect_url = league_obj.redirect_url,
            client_secret = league_obj.client_secret)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body)

    #store the oauth credentials in our flask session
    for key, val in resp.json().iteritems():
        session[key] = val

    #work around until I handle refresh tokens
    with open('backup/tokens.py','w') as f:
        f.write('tokens = {0}'.format(json.dumps(resp.json(), indent=2)))

    return redirect(url_for('leaguer'))

#figure out how this will work
@app.route('/refresh')
def refresh():
    league_obj = league(session['league_id'])

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_refresh_token_request(
        league.request_token_url,
        refresh_token = session['refresh_token'],
        client_id = league_obj.client_id,
        client_secret = league_obj.client_secret,
        redirect_uri = league_obj.redirect_url)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body) 

    with open('tokens2.py','w') as f:
        f.write('tokens = {0}'.format(json.dumps(resp.json(), indent=2)))

    #store the oauth credentials in our flask session
    for key, val in resp.json().iteritems():
        session[key] = val

    return redirect(url_for('leaguer'))

@app.route('/leaguer')
def leaguer():
    league_obj = league(session['league_id'])

    payload = {
        'format': 'json',
        'access_token': tokens['access_token'],
        'use_login': '1',
    }
    players_url = '{0}/league/{1}.l.{2}/players'.format(v2_url, '390', session['league_id'])

    start = 0
    count_per = 25
    status_code = 200

    while status_code == 200:

        url = '{0};count={1};start={2}'.format(players_url, count_per, start)
        resp = requests.get(url.format(start), params=payload)

        if resp.status_code == 401:
            new_tokens = refresh(tokens['refresh_token'])
            status_code = 200
            payload['access_token'] = new_tokens['access_token']
            print 'payload',payload
            print 'new_tokens',new_tokens
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


