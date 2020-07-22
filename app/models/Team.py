from app import db

class Team(db.Model):
    __tablename__ = 'team'

    pk = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, unique=True) #9
    team_key = db.Column(db.String(30), unique=True, index=True) #399.l.11609.t.9
    team_name = db.Column(db.String(40)) #Thx for the F shack
    team_url = db.Column(db.VARCHAR) #https://football.fantasysports.yahoo.com/f1/11609/9
    team_logo = db.Column(db.VARCHAR) #https://s.yimg.com/cv/apiv2/default/nfl/nfl_1.png
    waiver_priority = db.Column(db.String(4)) #
    number_of_moves = db.Column(db.String(5)) #0
    number_of_trades = db.Column(db.String(5)) #0
    league_scoring_type = db.Column(db.String(20)) #head
    has_draft_grade = db.Column(db.String(5)) #0

    manager1_nickname = db.Column(db.String(30)) #Terrence
    manager1_is_commissioner = db.Column(db.String(1)) #1
    manager1_image_url = db.Column(db.VARCHAR) #https://s.yimg.com/ag/images/default_user_profile_pic_64sq.jpg
    manager1_id = db.Column(db.String(10)) #9
    manager1_email = db.Column(db.String(100)) #cpuengineer5@yahoo.com

    manager2_nickname = db.Column(db.String(30)) #Terrence
    manager2_is_commissioner = db.Column(db.String(1)) #1
    manager2_image_url = db.Column(db.VARCHAR) #https://s.yimg.com/ag/images/default_user_profile_pic_64sq.jpg
    manager2_id = db.Column(db.String(10)) #9
    manager2_email = db.Column(db.String(100)) #cpuengineer5@yahoo.com

    def __repr__(self):
        return '{0}, managed by {1}'.format(self.team_name, self.manager1_nickname)

    def __init__(self, d):
        p = d['fantasy_content']['users']['0']['user'][1]['teams']
        for tid, team_dct in p.iteritems():

            if tid == 'count':
                continue
            
            team = team_dct['team']
            if isinstance(team, dict):
                try:
                    url = team['url']
                except KeyError:
                    continue
                name = team['name']
                team_key = team['team_key']


            else:

                for item in team_dct['team']:
                    for dct in item:
                        if 'team_logos' in dct:

                        print 'dct',dct
                        #print tid, team_dct['team']['name'], team_dct['team']['team_key']
                        print
                    break
                break
        
    

    '''
    dct {u'team_key': u'399.l.11609.t.9'}

    dct {u'team_id': u'9'}

    dct {u'name': u'Thx for the F shack'}

    dct {u'is_owned_by_current_login': 1}

    dct {u'url': u'https://football.fantasysports.yahoo.com/f1/11609/9'}

    dct {u'team_logos': [{u'team_logo': {u'url': u'https://s.yimg.com/cv/apiv2/default/nfl/nfl_1.png', u'size': u'large'}}]}

    dct []

    dct {u'waiver_priority': u''}

    dct []

    dct {u'number_of_moves': 0}

    dct {u'number_of_trades': 0}

    dct {u'roster_adds': {u'coverage_type': u'week', u'coverage_value': u'1', u'value': u'0'}}

    dct []

    dct {u'league_scoring_type': u'head'}

    dct []

    dct []

    dct {u'has_draft_grade': 0}

    dct []

    dct []

    dct {u'managers': [{u'manager': {u'nickname': u'Terrence', u'is_commissioner': u'1', u'image_url': u'https://s.yimg.com/ag/images/default_user_profile_pic_64sq.jpg', u'manager_id': u'9', u'guid': u'TZXDXM5R66MQIM7FAZ3YR5J55A', u'is_current_login': u'1', u'email': u'cpuengineer5@yahoo.com'}}]}


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

        p = d['fantasy_content']['league'][1]['players']['0']['player'][0]

        dct = {}
        for item in p:

            if not isinstance(item, dict):
                continue

            elif any([ item.get(key)
                for key in ('headshot','eligible_positions','image_url') ]):
                    continue

            elif item.get('name'):
                for name_key, value in item.get('name').iteritems():
                    dct['name_{0}'.format(name_key)] = value

            elif item.get('bye_weeks'):
                dct['bye_week'] = item['bye_weeks']['week']

            #suppressing because this is league dependent
            #elif item.get('eligible_positions'):
            #    dct['eligible_positions'] = ', '.join([
            #        pos.values()[0] for pos in item['eligible_positions'] ])

            else:
                dct.update(item)

        self.__dict__.update(dct)


