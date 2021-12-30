import os
import requests
import json
import datetime

# API documentation: https://www.api-football.com/documentation-v3#operation/get-fixtures

payload={}
headers = {
  'x-rapidapi-key': os.environ['football-api-key'],
  'x-rapidapi-host': 'v3.football.api-sports.io'
}

# pull the whole season of EPL fixtures
fixtures_url = "https://v3.football.api-sports.io/fixtures?league=39&season=2021"
fixtures_response = requests.request("GET", fixtures_url, headers=headers, data=payload)
fixtures = json.loads(fixtures_response.text)['response']

# pull the names of the 38 rounds, according to the API
rounds_url = "https://v3.football.api-sports.io/fixtures/rounds?league=39&season=2021"
rounds_response = requests.request("GET", rounds_url, headers=headers, data=payload)
rounds = json.loads(rounds_response.text)['response']

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
time_to_next_round = round_times[next_round] - datetime.datetime.now(datetime.timezone.utc)]

# print out the fixtures for next round – this'll be the basis of the message sent to telgram
fixtures = [fixture for fixture in fixtures if fixture['league']['round'] == next_round]
for fixture in fixtures:
  fixture_time_string = datetime.datetime.strftime(datetime.datetime.strptime(fixture['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z"), "%a %H:%M")
  print(f"{fixture['teams']['home']['name']} v {fixture['teams']['away']['name']} ({fixture_time_string})")

