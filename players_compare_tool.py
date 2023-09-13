# pry tool:  ipdb.set_trace()

import requests
import sys
import ipdb
import os
import json
import pprint

APIS = {
  'tank': "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerInfo",
  'espn': 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/athletes/pid/statistics/0?lang=en&region=us'
}

def tank_parser(url, headers, p1, p2):
  players = [p1, p2]
  players_data = []
  for item in players:
    data = requests.get(url, headers=headers, params=item).json()['body'][0]
    tank_data = {'tank': {
      'name': data['espnName'],
      'position': data['pos'],
      'espn_id': data['espnID'],
      'cbs_id': data['cbsPlayerID'],
      'rotowire_id': data['rotoWirePlayerID'],
      'yahoo_id': data['yahooPlayerID']
    }}
    players_data.append(tank_data)
  return players_data

def espn_parser(url, p1_id, p2_id, p1_pos, p2_pos):
  split_url = url.split('pid')
  player_list = [{"p_id": p1_id, "pos": p1_pos}, {"p_id": p2_id, "pos": p2_pos}]
  players_data = []
  for index, item in enumerate(player_list):
    i = index + 1
    pos = item['pos']
    espn_url = split_url[0] + item['p_id'] + split_url[1]
    data = requests.get(espn_url).json()['splits']['categories']
    general = next(item for item in data if item['displayName'] == 'General')['stats']
    fumbles = next(item for item in general if item['displayName'] == 'Fumbles')['value']
    games_played = next(item for item in general if item['displayName'] == 'Games Played')['value']
    scoring = next(item for item in data if item['displayName'] == 'Scoring')['stats']
    receiving = next(item for item in data if item['displayName'] == 'Receiving')['stats']
    rushing = next(item for item in data if item['displayName'] == 'Rushing')['stats']
    passing = next(item for item in data if item['displayName'] == 'Passing')['stats']
    espn_data = {'espn': {
      'scoring': scoring,
      'games_played': games_played,
      'fumbles': fumbles,
      'receiving': receiving,
      'rushing': rushing,
      'passing': passing
    }}
    players_data.append(espn_data)
  return players_data

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