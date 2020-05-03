import requests
from app import app
from app.User import User
from oauthlib.oauth2 import WebApplicationClient
from flask import redirect, request, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user

class yahoo_oauth2(object):
    #app_id = "HpucOz7i" #do i need this?

    base_url = "https://football.fantasysports.yahoo.com/f1"
    v2_url = "https://fantasysports.yahooapis.com/fantasy/v2"

    oauth2_base_url = "https://api.login.yahoo.com/oauth2"
    request_auth_url = "{0}/request_auth".format(oauth2_base_url)
    request_token_url = "{0}/get_token".format(oauth2_base_url) #doubles as refresh token url

    client_secret = "30cbbae3cdf91d86d986bf5c08df5fb9bcf95acb"
    client_id = "dj0yJmk9ZkJpU2FlS2c3TWZFJmQ9WVdrOVNIQjFZMDk2TjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTNi"

    redirect_url = "https://127.0.0.1:{0}/callback".format(app.config['PORT'])


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/login', methods=['GET','POST'])
def login():

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
    client = WebApplicationClient(yahoo_oauth2.client_id)
    req = client.prepare_authorization_request(
            yahoo_oauth2.request_auth_url,
            redirect_url = yahoo_oauth2.redirect_url)

    auth_url, headers, body = req
    return redirect(auth_url)

@app.route('/callback', methods=['GET','POST'])
def callback():
    '''
    Exchange authorization code for access token
     Send: client_id, client_secret, redirect_uricode, grant_type
     Receive: access_token, token_type, expire_in, refresh_token, xoauth_yahoo_guid
    '''
    client = WebApplicationClient(yahoo_oauth2.client_id)
    req = client.prepare_token_request(
            yahoo_oauth2.request_token_url,
            authorization_response=request.url, ##what is this?
            redirect_url = yahoo_oauth2.redirect_url,
            client_secret = yahoo_oauth2.client_secret)

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
    client = WebApplicationClient(yahoo_oauth2.client_id)
    req = client.prepare_refresh_token_request(
        yahoo_oauth2.request_token_url,
        refresh_token = current_user.refresh_token,
        client_id = yahoo_oauth2.client_id,
        client_secret = yahoo_oauth2.client_secret,
        redirect_uri = yahoo_oauth2.redirect_url)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body) 

    #permanently store user's oauth credentials
    current_user.set_tokens(resp.json())
    current_user.persist_user()

    return redirect(url_for('get_user_leagues'))