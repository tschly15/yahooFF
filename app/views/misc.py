#!/usr/bin/env python
import json
import dpath
import requests
from app import app
from app.models.Misc import yahoo_oauth2
from app.views.authentication import refresh
from flask_login import current_user, login_required
from flask import redirect, request, url_for, session, render_template

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

        #team_key format: 390.l.137260.t.6 or 389.t.3081322
        team_key = getattr(self, 'team_key', None)
        if team_key is None:
            return

        #we now have the team key, so get the league information
        url = '{0}/league/{1}'.format(yahoo_oauth2.v2_url, team_key.rsplit('.',2)[0])

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

        #identify leagues preceding/following league id (if applicable)
        league_renew = league_dict['renew']
        league_renewed = league_dict['renewed']

        #print "Welcome to {0} {1}!\nVisit at {2}".format(league_name, league_season, league_url)


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
    manager_leagues = "{0}/users;use_login=1;game_keys=nfl/teams".format(yahoo_oauth2.v2_url)
    manager_current_league = "{0}/users;use_login=1/games;game_keys=nfl/teams".format(yahoo_oauth2.v2_url)

    def __init__(self, league_id):
        self.url = "{0}/{1}".format(yahoo_oauth2.base_url, league_id)

@app.route('/get_user_leagues', methods=['GET','POST'])
@login_required
def get_user_leagues():

    payload = {
        'format': 'json',
        'access_token': current_user.access_token,
    }

    #TODO: wrap the response 401 functionality
    #will try to pull out the NFL teams for the logged-in user
    resp = requests.get(league.manager_leagues, params=payload)

    #received an Unauthorized response
    if resp.status_code == 401:

        if not current_user.refresh_token.strip():
            return redirect(url_for('request_auth'))
        else:
            # renew our credentials ...
            refresh() 
            payload['access_token'] = current_user.access_token

            # ... then try one more time
            resp = requests.get(league.manager_leagues, params=payload)
    ##############################

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
