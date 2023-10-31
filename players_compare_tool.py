# pry tool:  ipdb.set_trace()

import requests
import sys
import ipdb
import os
import json
import pprint
from alive_progress import alive_bar
import time

APIS = {
  'tank': "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerInfo",
  'espn': 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/athletes/pid/statistics/0?lang=en&region=us'
}

def tank_parser(url, headers, p1, p2):
  players = [p1, p2]
  players_data = []
  for player in players:
    data = requests.get(url, headers=headers, params=player).json()['body'][0]
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
  for player in player_list:
    espn_data = {'espn': {}}
    espn_url = split_url[0] + player['p_id'] + split_url[1]
    data = requests.get(espn_url).json()['splits']['categories']
    for item in data:
      cat = item['displayName']
      if cat == 'General':
        espn_data['espn'][cat] = {}
        stats = item['stats']
        espn_data['espn'][cat]['games_played'] = next(i for i in stats if i['name'] == 'gamesPlayed')['value']
        espn_data['espn'][cat]['fumbles'] = next(i for i in stats if i['name'] == 'fumbles')['value']
      elif (p1_pos == 'QB' and p2_pos == 'QB') and cat == 'Passing':
        espn_data['espn'][cat] = {}
        stats = item['stats']
        stat_names = ['completionPct', 'completions', 'interceptionPct', 'interceptions', 'passingAttempts', 'passingBigPlays', 'passingTouchdownPct', 'passingTouchdowns', 'passingYards', 
                  'passingYardsAtCatch', 'passingYardsPerGame', 'QBRating', 'sacks', 'sackYardsLost', 'totalTouchdowns', 'totalYardsFromScrimmage', 'yardsFromScrimmagePerGame', 'yardsPerGame']
        for i in stats:
          name = i['name']
          if name in stat_names:
            espn_data['espn'][cat][name] = i['value']
      elif (p1_pos != 'QB' and p2_pos != 'QB') and cat == 'Rushing':
        espn_data['espn'][cat] = {}
        stats = item['stats']
        stat_names = ['ESPNRBRating', 'netYardsPerGame', 'rushingAttempts', 'rushingBigPlays', 'rushingFirstDowns', 'rushingFirstDowns', 'rushingYardsPerGame', 'rushingTouchdowns', 
                      'stuffs', 'totalTouchdowns', 'totalYards', 'yardsPerGame', 'yardsPerRushAttempt']
        for i in stats:
          name = i['name']
          if name in stat_names:
            espn_data['espn'][cat][name] = i['value']
      elif (p1_pos != 'QB' and p2_pos != 'QB') and cat == 'Receiving':
        espn_data['espn'][cat] = {}
        stats = item['stats']
        stat_names = ['ESPNWRRating', 'netTotalYards', 'netYardsPerGame', 'receivingBigPlays', 'receivingTargets', 'receivingTouchdowns', 'receivingYards', 'receivingYardsAfterCatch',
                      'receivingYardsPerGame', 'receptions', 'totalPointsPerGame', 'totalTouchdowns', 'totalYards', 'yardsPerGame', 'yardsPerReception']
        for i in stats:
          name = i['name']
          if name in stat_names:
            espn_data['espn'][cat][name] = i['value']
    players_data.append(espn_data)
    ipdb.set_trace()
  return players_data

# def espn_players_compare(player1, player2):
#   p1 = player1[1]['espn']
#   p2 = player2[1]['espn']
#   for key, value in p1.items():
#     ipdb.set_trace()

def compare_players(player1, player2):
  split_player1 = player1.split('_')
  split_player2 = player2.split('_')
  player1_fullname = ' '.join(split_player1)
  player2_fullname = ' '.join(split_player2)
  player1_list = []
  player2_list = []
  # with alive_bar(3) as bar:
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
      # bar()
    elif value == 'espn':
      p1_pos = player1_list[0]['tank']['position']
      p2_pos = player2_list[0]['tank']['position']
      p1_espn_id = player1_list[0]['tank']['espn_id']
      p2_espn_id = player2_list[0]['tank']['espn_id']
      espn_data = espn_parser(url, p1_espn_id, p2_espn_id, p1_pos, p2_pos)
      player1_list.append(espn_data[0])
      player2_list.append(espn_data[1])
      # bar()soun
  # espn_players_compare(player1_list, player2_list)
  # bar()
  # ipdb.set_trace()
  print(player1_fullname)  
  pprint.pprint(player1_list)
  print('-----------------------------')
  print(player2_fullname)
  pprint.pprint(player2_list)

def main():
  player1 = sys.argv[1]
  player2 = sys.argv[2]
  compare_players(player1, player2)
    

if __name__ == "__main__":
  main()