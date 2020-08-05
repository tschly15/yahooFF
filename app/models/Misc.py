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
    teams_url = v2_url + '/users;use_login=1;game_keys=nfl/teams'

    player_url = '{0}/players;start={1};count={2}/draft_analysis'
