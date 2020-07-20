import requests
from app import app
from app.models.Misc import yahoo_oauth2
from flask import redirect, request, url_for, render_template, abort
from flask_login import current_user, login_user, login_required, logout_user

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
    num_teams = len(d['fantasy_content']['users']['0']['user'][1]['teams'])
    return '{0} owns {1} teams'.format(current_user.user_name, num_teams)
