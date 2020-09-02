from app import app

class yahoo_oauth2(object):
    base_url = "https://football.fantasysports.yahoo.com/f1"
    v2_url = "https://fantasysports.yahooapis.com/fantasy/v2"

    oauth2_base_url = "https://api.login.yahoo.com/oauth2"
    request_auth_url = "{0}/request_auth".format(oauth2_base_url)
    request_token_url = "{0}/get_token".format(oauth2_base_url) #doubles as refresh token url

    #Yahoo App listed as port 5000
    redirect_url = "https://127.0.0.1:{0}/callback".format(app.config['PORT'])

    league_url = v2_url + '/league/'
    user_teams_url = v2_url + '/users;use_login=1;game_keys=nfl/teams'

    team_url = '{0}/team/{1}'
    player_url = '{0}/players;start={1};count={2}/draft_analysis'

    #retrieve all teams belonging to league
    all_teams_url = v2_url + '/league/{0}/teams' #league_key

    #retrieve players using team context ... 
    roster_url = v2_url + '/team/{0}/roster/players' #team_key
    #... and their weekly stats
    player_weekly_stats_url = v2_url + '/league/{0}/players;player_keys={1}/stats;type=week;week={2}' #league_key, player_key, week

    #draft results - team context
    team_draft_url = v2_url + '/team/{0}/draftresults' #team_key
    #draft results - league context
    league_draft_url = v2_url + '/league/{0}/draftresults' #league_key
