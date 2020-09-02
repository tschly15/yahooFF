import requests
from app import app, db
from app.models.User import User
from app.models.Misc import yahoo_oauth2
from oauthlib.oauth2 import WebApplicationClient
from flask import redirect, request, url_for, render_template, flash
from flask_login import current_user, login_user, login_required, logout_user

@app.route('/login', methods=['GET','POST'])
def login():
    '''
    log into my site
    '''

    #alleviate cookie issues by always logging out
    if current_user.is_authenticated:
        logout_user()
        flash("Logged you out")
        return redirect(url_for('login'))

    if request.method == 'POST':
        input_name = request.form['user_name']
        input_password = request.form['user_password']

        #check if User exists in the database
        user = User.query.filter_by(user_name=input_name).first()
        if user is None or not user.check_password(input_password):
            flash("Invalid username or password")
            return redirect(url_for('login'))

        login_user(user)

        next_page = request.args.get('next')
        if not (next_page and url_parse(next_page).netloc):
            next_page = url_for('user_home')
        return redirect(next_page)

    return render_template('login.html')

@login_required
@app.route('/user_home', methods=['GET','POST'])
def user_home():
    ''' log into Yahoo '''

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    access_token = current_user.user_access_token.strip()
    if access_token:
        return redirect(url_for('teams'))

    #attempt to refresh a stale Yahoo session
    refresh_token = current_user.user_refresh_token.strip()
    if refresh_token:
        return redirect(url_for('refresh'))

    #send them to login at Yahoo
    return render_template('yahoo.html')

@app.route('/request_auth', methods=['GET'])
def request_auth():
    '''
    Request an authorization URL
     Send: client_id, redirect_uri, response_type
     Receive: authorization code
    '''
    client = WebApplicationClient(app.config['CLIENT_ID'])
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
    client = WebApplicationClient(app.config['CLIENT_ID'])
    req = client.prepare_token_request(
            yahoo_oauth2.request_token_url,
            authorization_response=request.url, ##what is this?
            redirect_url = yahoo_oauth2.redirect_url,
            client_secret = app.config['CLIENT_SECRET'])

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body)

    #update the user object with the (response) token data
    current_user.set_oauth_tokens(resp.json())

    #permanently store user's oauth credentials
    db.session.add(current_user)
    db.session.commit()

    return redirect(url_for('teams'))

@app.route('/refresh', methods=['GET','POST'])
def refresh():
    '''
    Exchange refresh token for a new access token
     Send: client_id, client_secret, redirect_uri, refresh_token, grant_type
     Receive: access_token, token_type, expire_in, refresh_token, xoauth_yahoo_guid
    Note: only the access_token will change (refresh_token does not change)
    '''
    client = WebApplicationClient(app.config['CLIENT_ID'])
    req = client.prepare_refresh_token_request(
        yahoo_oauth2.request_token_url,
        refresh_token = current_user.user_refresh_token,
        client_id = app.config['CLIENT_ID'],
        client_secret = app.config['CLIENT_SECRET'],
        redirect_uri = yahoo_oauth2.redirect_url)

    token_url, headers, body = req
    resp = requests.post(token_url, headers=headers, data=body) 

    if resp.status_code == 400:
        abort(400, resp.json()['error'])

    #update the user object with the (response) token data
    current_user.set_oauth_tokens(resp.json())

    #permanently store user's oauth credentials
    db.session.add(current_user)
    db.session.commit()

    return redirect(url_for('teams'))

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(400)
def custom_400(error):
    '''remove tokens to force login'''

    current_user.user_access_token = ''
    current_user.user_refresh_token = ''
    try:
        db.session.add(current_user)
        db.session.commit()
    except Exception as e:
        print e.args
    
    flash("Your Yahoo! credentials were invalid. Please login")
    return redirect(url_for('user_home'))

@app.errorhandler(401)
def custom_401(error):
    '''
    remove user's access token
    their refresh token may get them back in
    '''
    current_user.user_access_token = ''
    db.session.add(current_user)
    db.session.commit()
    
    flash("Your Yahoo! credentials have expired. Please login")
    return redirect(url_for('user_home'))
