import requests
import os.path


class FrcApi:
    def __init__(self, server, username, auth_token):
        if server == 'prod':
            self.base_url = 'https://frc-api.firstinspires.org/v2.0/' 
        elif server == 'stage':
            self.base_url = 'https://frc-staging-api.firstinspires.org/v2.0/' 
        else:
            raise Exception("prod is the only option for server")
        self.username = username
        self.auth_token = auth_token
        if self.username is not None and self.auth_token is not None:
            self.headers = {
                'Accept': 'application/json', 
                'Authorization': self.auth_token
            }
            self.auth = (username, self.auth_token)
        elif(username == None and self.auth_token ==  None):
            self.headers = {
                'Accept': 'application/json'
            }
            self.auth = ()
        else:
            raise ValueError(
                "Your set_up request was malformed. "+
                "It either need both a username and auth_token or none " +
                "of those (if working on the mock server)")

    def get_endpoint(self, url, payload):
        r = requests.get(url, 
                params=payload, headers=self.headers, auth=self.auth)
        if(r.status_code != 200):
            r.raise_for_status()
        else:
            data = r.json()
            return data

    def get_alliance_selection(self, season, eventCode):
        verify_year(season)
        url = os.path.join(
            self.base_url, str(season), 'alliances', eventCode)
        return self.get_endpoint(url, {})

    def get_event_awards(self, season, eventCode=None, teamNumber=None):
        verify_year(season)
        paths = [x for x in [eventCode, teamNumber] if x is not None]
        assert len(paths) != 0, "specify at least one of eventCode, teamNumber"
        url = os.path.join(self.base_url, str(season), 'awards', *paths)
        return self.get_endpoint(url, {})

    def get_award_listings(self, season):
        url = os.path.join(self.base_url, str(season), 'awards', 'list')
        return self.get_endpoint(url, {})

    def get_ancillary(self):
        """
        Returns basic info about the API. 
        """
        return self.get_endpoint(self.base_url, {})

    def get_event_match_results(self, season, eventCode, 
            teamNumber=None, tournamentLevel=None, matchNumber=None, 
            start=None, end=None):
        payload = {}
        verify_year(season)
        if(tournamentLevel is not None):
            verify_tournament_level(tournamentLevel)
        if(matchNumber is not None or start is not None or end is not None):
            if(tournamentLevel is None):
                raise ValueError(
                    'If you supply a matchNumber, start, ' +
                    'or end parameter then you must supply a tournamentLevel')
        if(teamNumber is not None and matchNumber is not None):
            raise ValueError(
                'You can not supply both a teamNumber and a matchNumber')
        if(matchNumber is not None and start is not None):
            raise ValueError("You can't specify both a matchNumber and start")
        if(matchNumber is not None and end is not None):
            raise ValueError("You can't specify both a matchNumber and end")
        if(teamNumber is not None):
            payload['teamNumber'] = teamNumber
        if(tournamentLevel is not None):
            payload['tournamentLevel'] = tournamentLevel
        if(matchNumber is not None):
            payload['matchNumber'] = matchNumber
        if(start is not None):
            payload['start'] = start
        if(end is not None):
            payload['end'] = end
        url = os.path.join(self.base_url, str(season), 'matches', eventCode)
        return self.get_endpoint(url, payload)

    def get_score_details(self, season, eventCode, tournamentLevel,
            teamNumber=None, matchNumber=None, start=None, end=None):
        verify_year(season)
        verify_tournament_level(tournamentLevel)
        payload = {}
        if teamNumber is not None:
            msg = 'teamNumber is mutually exclusive to matchNumber'
            assert matchNumber is None, msg
            payload['teamNumber'] = teamNumber
        if matchNumber is not None:
            msg = 'matchNumber is mutually exclusive to start'
            assert start is None, msg
            msg = 'matchNumber is mutually exclusive to end'
            assert end is None, msg
            payload['matchNumber'] = matchNumber
        if start is not None:
            payload['start'] = start
        if end is not None:
            payload['end'] = end
        url = os.path.join(
            self.base_url, str(season), 'scores', eventCode, tournamentLevel)
        return self.get_endpoint(url, payload)

    def get_event_rankings(self, season, eventCode, 
            teamNumber=None, top=None):
        verify_year(season)
        payload = {}
        if(teamNumber is not None):
            payload['teamNumber'] = teamNumber
        if(top is not None):
            payload['top'] = top
        if(teamNumber is not None and top is not None):
            raise ValueError("You cant supply both a teamNumber and a top parameter")
        url = os.path.join(
            self.base_url, str(season), 'rankings', eventCode)
        return self.get_endpoint(url, payload)

    def get_event_schedule(self, season, eventCode,
            tournamentLevel, teamNumber=None, start= None, end=None):
        """
        'The schedule API returns the match schedule for the desired tournament 
         level of a particular event in a particular season.'
        Parameters: 
        eventCode: 
            The event code for the event you wish to get the schedule for. 
            EX: ILIL
        tournamentLevel: 
            The type of schedule you want to return. 
            Can be either 'qual' or 'elim'
        
        Returns:
        A python dictionary converted from the JSON.
        
        Example calls:
        getEventSchedule('ilil, 'qual')  #Without teamnumber
        getEventSchedule('ilil', 'qual', )
        """
        verify_year(season)
        verify_tournament_level(tournamentLevel)
        payload = {}
        payload['tournamentLevel'] = tournamentLevel
        if (teamNumber != None):
            payload['teamNumber'] = teamNumber
        if (start != None):
            payload['start'] = start
        if (end != None):
            payload['end'] = end
        url = os.path.join(
            self.base_url, str(season), 'schedule', eventCode)
        return self.get_endpoint(url, payload)

    def get_hybrid_event_schedule(self, season, eventCode, 
            tournamentLevel, start=None, end=None):
        verify_year(season)
        verify_tournament_level(tournamentLevel)
        payload = {}
        if (start is not None):
            payload['start'] = start
        if (end is not None):
            payload['end'] = end
        url = os.path.join(
            self.base_url, str(season), 'schedule', eventCode, 
            tournamentLevel, 'hybrid')
        return self.get_endpoint(url, payload)

    def get_season_summary(self, season):
        verify_year(season)
        url = os.path.join(self.base_url, str(season))
        return self.get_endpoint(url, {})

    def get_event_listings(self, 
            season,
            eventCode=None, 
            teamNumber=None, 
            districtCode=None,
            excludeDistrict=None):
        payload = {}
        if eventCode is not None:
            msg = 'eventCode is mutually exclusive to any other parameter'
            assert teamNumber is None, msg
            assert districtCode is None, msg
            assert excludeDistrict is None, msg
            payload['eventCode'] = eventCode
        if districtCode is not None:
            msg = 'districtCode is mutually exclusive to excludeDistrict'
            assert excludeDistrict is None, msg
            payload['districtCode'] = districtCode
        if teamNumber is not None:
            payload['teamNumber'] = teamNumber
        if excludeDistrict is not None:
            payload['excludeDistrict'] = excludeDistrict
        verify_year(season)
        url = os.path.join(self.base_url, str(season), "events")
        return self.get_endpoint(url, payload)

    def get_district_listings(self, season):
        verify_year(season)
        url = os.path.join(self.base_url, str(season), "districts")
        return self.get_endpoint(url, {})

    def get_team_listings(self, season, teamNumber=None, eventCode=None, districtCode=None, page=None):
        if(teamNumber is not None and eventCode is not None):
            raise ValueError('You can\'t supply both a teamnumber and an eventCode')
        if(teamNumber is not None and districtCode is not None):
            raise ValueError('You can\'t supply both a teamnumber and an districtCode')
        verify_year(season)
        payload = {}
        if (teamNumber is not None):
            payload['teamNumber'] = teamNumber
        if (eventCode is not None):
            payload['eventCode'] = eventCode
        if (districtCode is not None):
            payload['districtCode'] = districtCode
        if (page is not None):
            payload['page'] = page
        url = os.path.join(self.base_url, str(season), "teams")
        return self.get_endpoint(url, payload)


###HELPER FUNCTIONS###
def verify_year(season):
    '''
    This class is to make sure the year is valid according the the API specs
    '''
    if(type(season) is int):
        if(len(str(season)) != 4):
            raise ValueError('Year must be four digits')
        if(season-2014 < 0):
            raise ValueError('Year must be greater than 2014')
    else:
        raise ValueError('Year must be an integer')
    return 1


def verify_tournament_level(tournamentLevel):
    if(type(tournamentLevel) is str):
        if (tournamentLevel == 'qual' or tournamentLevel == 'playoff'):
            return 1
        else:
            raise ValueError('tournamentLevel must either be "qual" or "playoff"')
    else:
        raise ValueError('tournamentLevel must be a string')

