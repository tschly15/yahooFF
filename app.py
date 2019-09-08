#!/usr/bin/env python
import requests
from oauthlib.oauth2 import WebApplicationClient
from flask import Flask, redirect, request, url_for, session

#TODO:
#refresh the token

app = Flask(__name__)
app.secret_key = b'hdknbvmsebnapwema/daf864adfa1'

class league(object):
    base_url = "https://football.fantasysports.yahoo.com/f1"
    request_auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
    request_token_url = 'https://api.login.yahoo.com/oauth2/get_token'

    def __init__(self, league_id):
        self.app_id = "HpucOz7i"
        self.url = "{0}/{1}".format(league.base_url, league_id)

        self.client_secret = "30cbbae3cdf91d86d986bf5c08df5fb9bcf95acb"
        self.client_id = "dj0yJmk9ZkJpU2FlS2c3TWZFJmQ9WVdrOVNIQjFZMDk2TjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTNi"

        self.redirect_url = "https://127.0.0.1:5000/callback"


@app.route('/')
def home():
    return '''
    <html>
        <body>
            <form method="get" action="redirector">
                <button type="submit">Click to Login at Yahoo</button>
            </form>
        </body>
    </html>'''

@app.route('/redirector')
def redirector(methods=['GET']):
    league_id = 137260
    league_obj = league(league_id)

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_authorization_request(
            league.request_auth_url,
            redirect_url = league_obj.redirect_url)

    auth_url, headers, body = req
    return redirect(auth_url)

@app.route('/callback')
def callback():

    league_id = 137260
    league_obj = league(league_id)

    client = WebApplicationClient(league_obj.client_id)
    req = client.prepare_token_request(
            league.request_token_url,
            authorization_response=request.url,
            redirect_url = league_obj.redirect_url,
            client_secret = league_obj.client_secret)

    auth_url, headers, body = req
    resp = requests.post(auth_url, headers=headers, data=body)

    #store the oauth credentials in our flask session
    for key, val in resp.json().iteritems():
        session[key] = val

    return redirect(url_for('leaguer'))


@app.route('/leaguer')
def leaguer():
    league_id = 137260
    league_obj = league(league_id)

    url = "https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l."
    payload = {
        'format': 'json',
        'access_token': session['access_token'],
    }

    resp = requests.get(url.format(league_id),
                        params=payload)
    result = resp.json()

    return result

app.run(debug=True, ssl_context='adhoc')
