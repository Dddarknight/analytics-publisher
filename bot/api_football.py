import aiohttp
import os
from dotenv import load_dotenv


load_dotenv()

URL = 'https://v3.football.api-sports.io/teams'
LEAGUE = 39
SEASON = 2022
API_KEY = os.getenv('API_FOOTBALL')


async def get_premier_league_teams():
    params = {
        'league': LEAGUE,
        'season': SEASON
    }
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
                URL, params=params, headers=headers) as response:
            data = await response.json()
            return get_teams(data)


def get_teams(data):
    teams = [team['team']['name'] for team in data['response']]
    return teams
