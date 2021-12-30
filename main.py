import os
import requests
import json
import datetime
from replit import db

# API documentation: https://www.api-football.com/documentation-v3#operation/get-fixtures

payload={}
headers = {
  'x-rapidapi-key': os.environ['football-api-key'],
  'x-rapidapi-host': 'v3.football.api-sports.io'
}

LEAGUEID = 39 # EPL
SEASON = 2021

# pull the whole season of EPL fixtures
try:
  fixtures = db['fixtures']
  print('Loaded fixtures from database')
except KeyError:
  fixtures_url = f"https://v3.football.api-sports.io/fixtures?league={LEAGUEID}&season={SEASON}"
  fixtures_response = requests.request("GET", fixtures_url, headers=headers, data=payload)
  fixtures = json.loads(fixtures_response.text)['response']
  db['fixtures'] = fixtures
  print('Loaded fixtures from API')

#TODO: periodically refresh the fixtures, in case they change

# pull the names of the 38 rounds, according to the API
try:
  rounds = db['rounds']
  print('Loaded rounds from database')
except KeyError:
  rounds_url = f"https://v3.football.api-sports.io/fixtures/rounds?league={LEAGUEID}&season={SEASON}"
  rounds_response = requests.request("GET", rounds_url, headers=headers, data=payload)
  rounds = json.loads(rounds_response.text)['response']
  db['rounds'] = rounds
  print('Loaded rounds from API')

# for each round, calculate the first match. This'll be used for scheduling the
# telegram message when the next round starts in 24 hours
round_times = {}
for fixture in fixtures:
  fixture_round = fixture['league']['round'] 
  fixture_time = datetime.datetime.strptime(fixture['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
  if fixture_round not in round_times or round_times[fixture_round] >= fixture_time:
    round_times[fixture_round] = fixture_time

# identify the next round, and how long until it starts
next_round = [round for round in rounds if round_times[round] > datetime.datetime.now(datetime.timezone.utc)][0]
time_to_next_round = round_times[next_round] - datetime.datetime.now(datetime.timezone.utc)

# print out the fixtures for next round – this'll be the basis of the message sent to telgram
fixtures = [fixture for fixture in fixtures if fixture['league']['round'] == next_round]
for fixture in fixtures:
  fixture_time_string = datetime.datetime.strftime(datetime.datetime.strptime(fixture['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z"), "%a %H:%M")
  print(f"{fixture['teams']['home']['name']} v {fixture['teams']['away']['name']} ({fixture_time_string})")

