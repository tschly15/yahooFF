import requests
from app import app
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

    r = requests.get(yahoo_oauth2.teams_url, params=params)
    if r.status_code == 401:
        abort(401)

    d = r.json()
    for tid, team_dct in d['fantasy_content']['users']['0']['user'][1]['teams'].iteritems():

        if tid == 'count':
            continue
        
        if isinstance(team_dct['team'], dict):
            url = team_dct['url']
            name = team_dct['team']
            team_key = team_dct['team_key']

        else:

            for team in team_dct['team']:
                print team
                #print tid, team_dct['team']['name'], team_dct['team']['team_key']
                print
    
    
    num_teams = len(d['fantasy_content']['users']['0']['user'][1]['teams'])
    return '{0} owns {1} teams'.format(current_user.user_name, num_teams)

    '''
    [
      {"team_key": "390.l.137260.t.6" },
      {"team_id": "6" },
      {"name": "Thx for the F shack" },
      {"is_owned_by_current_login": 1 },
      { "url": "https://football.fantasysports.yahoo.com/2019/f1/137260/6" },
      {
        "team_logos": [
          {
            "team_logo": {
              "url": "https://s.yimg.com/cv/apiv2/default/nfl/nfl_1.png", 
              "size": "large"
            }
          }
        ]
      }, 
      [], 
      { "waiver_priority": 11 },
      [], 
      { "number_of_moves": "47" },
      { "number_of_trades": 0 },
      {
        "roster_adds": {
          "coverage_type": "week", 
          "coverage_value": "17", 
          "value": "0"
        }
      }, 
      { "clinched_playoffs": 1 },
      { "league_scoring_type": "head" },
      [], 
      [],
      {
        "draft_recap_url": "https://football.fantasysports.yahoo.com/2019/f1/137260/6/draftrecap",
        "draft_grade": "A",
        "has_draft_grade": 1
      },
      [],
      [],
      {
        "managers": [
          {
            "manager": {
              "is_current_login": "1",
              "image_url": "https://s.yimg.com/ag/images/default_user_profile_pic_64sq.jpg",
              "manager_id": "6",
              "guid": "TZXDXM5R66MQIM7FAZ3YR5J55A",
              "nickname": "Terrence",
              "email": "cpuengineer5@yahoo.com"
            }
          }
        ]
      }
    ]
    '''

