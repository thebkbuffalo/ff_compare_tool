# pry tool:  ipdb.set_trace()

import requests
import sys
import ipdb
import os
import json
import pprint

APIS = {
  'tank': "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerInfo",
  'espn': 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2022/types/2/athletes/pid/statistics/0?lang=en&region=us'
}

def tank_parser(url, headers, p1, p2):
  p1_return = requests.get(url, headers=headers, params=p1).json()['body'][0]
  p2_return = requests.get(url, headers=headers, params=p2).json()['body'][0]
  p1_data = {'tank': {
    'position': p1_return['pos'],
    'espn_id': p1_return['espnID'],
    'cbs_id': p1_return['cbsPlayerID'],
    'rotowire_id': p1_return['rotoWirePlayerID'],
    'yahoo_id': p1_return['yahooPlayerID']
  }}
  p2_data = {'tank': {
    'position': p2_return['pos'],
    'espn_id': p2_return['espnID'],
    'cbs_id': p2_return['cbsPlayerID'],
    'rotowire_id': p2_return['rotoWirePlayerID'],
    'yahoo_id': p2_return['yahooPlayerID']
  }}
  return [p1_data, p2_data]

def espn_parser(url, p1_id, p2_id, p1_pos, p2_pos):
  split_url = url.split('pid')
  p1_url = split_url[0] + p1_id + split_url[1]
  p2_url = split_url[0] + p2_id + split_url[1]
  # player 1 data
  p1_return = requests.get(p1_url).json()['splits']['categories']
  p1_general = next(item for item in p1_return if item['displayName'] == 'General')['stats']
  p1_fumbles = next(item for item in p1_general if item['displayName'] == 'Fumbles')
  p1_games_played = next(item for item in p1_general if item['displayName'] == 'Games Played')
  p1_scoring = next(item for item in p1_return if item['displayName'] == 'Scoring')['stats']
  p1_rushing = next(item for item in p1_return if item['displayName'] == 'Rushing')['stats']
  p1_receiving = next(item for item in p1_return if item['displayName'] == 'Receiving')['stats']
  p1_data = {'espn': {
    'scoring': p1_scoring,
    'games_played': p1_games_played,
    'fumbles': p1_fumbles
  }}
  if p1_pos == 'WR' or 'TE' or 'RB':
    p1_data['receiving'] = p1_receiving
  elif p1_pos == 'RB':
    p1_data['rushing'] = p1_rushing
  elif p1_pos == 'QB':
    p1_data['rushing'] = p1_rushing
    p1_data['passing'] = next(item for item in p1_return if item['displayName'] == 'Passing')['stats']
  # player 2 data
  p2_return = requests.get(p2_url).json()['splits']['categories']
  p2_general = next(item for item in p2_return if item['displayName'] == 'General')['stats']
  p2_fumbles = next(item for item in p2_general if item['displayName'] == 'Fumbles')
  p2_games_played = next(item for item in p2_general if item['displayName'] == 'Games Played')
  p2_scoring = next(item for item in p2_return if item['displayName'] == 'Scoring')['stats']
  p2_rushing = next(item for item in p2_return if item['displayName'] == 'Rushing')['stats']
  p2_receiving = next(item for item in p2_return if item['displayName'] == 'Receiving')['stats']
  p2_data = {'espn': {
    'scoring': p2_scoring,
    'games_played': p2_games_played,
    'fumbles': p2_fumbles
  }}
  if p2_pos == 'WR' or 'TE' or 'RB':
    p2_data['receiving'] = p2_receiving
  elif p2_pos == 'RB':
    p2_data['rushing'] = p2_rushing
  elif p2_pos == 'QB':
    p2_data['rushing'] = p2_rushing
    p2_data['passing'] = next(item for item in p2_return if item['displayName'] == 'Passing')['stats']
  
  return [p1_data, p2_data]

def compare_players(player1, player2):
  split_player1 = player1.split('_')
  split_player2 = player2.split('_')
  player1_fullname = ' '.join(split_player1)
  player2_fullname = ' '.join(split_player2)
  player1_list = []
  player2_list = []
  for key, value in enumerate(APIS):
    upcase_val = value.upper()
    url = APIS[value]
    player1_params = {'playerName': player1, 'getStats': 'true'}
    player2_params = {'playerName': player2, 'getStats': 'true'}
    key = os.getenv(upcase_val+'_KEY')
    host = os.getenv(upcase_val+'_HOST')
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
    if value == 'tank':
      tank_data = tank_parser(url, headers, player1_params, player2_params)
      player1_list.append(tank_data[0])
      player2_list.append(tank_data[1])
    elif value == 'espn':
      p1_pos = player1_list[0]['tank']['position']
      p2_pos = player2_list[0]['tank']['position']
      p1_espn_id = player1_list[0]['tank']['espn_id']
      p2_espn_id = player2_list[0]['tank']['espn_id']
      espn_data = espn_parser(url, p1_espn_id, p2_espn_id, p1_pos, p2_pos)
      player1_list.append(espn_data[0])
      player2_list.append(espn_data[1])
      
  ipdb.set_trace()
    # pprint.pprint(player1_list)
    # pprint.pprint(player2_list)

def main():
  player1 = sys.argv[1]
  player2 = sys.argv[2]
  compare_players(player1, player2)
    

if __name__ == "__main__":
  main()