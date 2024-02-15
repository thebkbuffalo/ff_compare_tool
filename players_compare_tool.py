# in progress fantasy football player compare tool

# pry tool:  ipdb.set_trace()

import requests
import sys
import ipdb
import os
import json
import pprint
from alive_progress import alive_bar
import time
import datetime

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
      'yahoo_id': data['yahooPlayerID'],
      'team': data['stats']['team']
    }}
    players_data.append(tank_data)
  return players_data

def matchups_parser(url, headers, params, teams):
  data = requests.get(url, headers=headers, params=params).json()['body']
  matchups_data = []
  for i, t in enumerate(teams):
    i += 1
    away = list(filter(lambda d: d['away'] == t, data))
    home = list(filter(lambda d: d['home'] == t, data))
    h_a = home[0] if len(home) == 1 else away[0]
    h_a_txt = 'home' if h_a['home'] == t else 'away'
    # ipdb.set_trace()
    team_matchup_data = {
      'home_or_away': h_a_txt,
      'gameID': h_a['gameID'],
      'espnID': h_a['espnID'],
      'opponent': h_a['home'] if h_a_txt == 'away' else h_a['away'],
      'gameDate': h_a['gameDate']
    }
    matchups_data.append(team_matchup_data)
  return matchups_data
      

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
        stats = item['stats']
        espn_data['espn']['General_games_played'] = next(i for i in stats if i['name'] == 'gamesPlayed')['value']
        espn_data['espn']['General_fumbles'] = next(i for i in stats if i['name'] == 'fumbles')['value']
      elif (p1_pos == 'QB' and p2_pos == 'QB') and cat == 'Passing':
        stats = item['stats']
        stat_names = ['completionPct', 'completions', 'interceptionPct', 'interceptions', 'passingAttempts', 'passingBigPlays', 'passingTouchdownPct', 'passingTouchdowns', 'passingYards', 
                  'passingYardsAtCatch', 'passingYardsPerGame', 'QBRating', 'sacks', 'sackYardsLost', 'totalTouchdowns', 'totalYardsFromScrimmage', 'yardsFromScrimmagePerGame', 'yardsPerGame']
        for i in stats:
          name = i['name']
          full_stat_name = cat+'_'+name
          if name in stat_names:
            espn_data['espn'][full_stat_name] = i['value']
      elif cat == 'Rushing':
        stats = item['stats']
        stat_names = ['ESPNRBRating', 'netYardsPerGame', 'rushingAttempts', 'rushingBigPlays', 'rushingFirstDowns', 'rushingFirstDowns', 'rushingYardsPerGame', 'rushingTouchdowns', 
                      'stuffs', 'totalTouchdowns', 'totalYards', 'yardsPerGame', 'yardsPerRushAttempt']
        for i in stats:
          name = i['name']
          full_stat_name = cat+'_'+name
          if name in stat_names:
            espn_data['espn'][full_stat_name] = i['value']
      elif (p1_pos != 'QB' and p2_pos != 'QB') and cat == 'Receiving':
        stats = item['stats']
        stat_names = ['ESPNWRRating', 'netTotalYards', 'netYardsPerGame', 'receivingBigPlays', 'receivingTargets', 'receivingTouchdowns', 'receivingYards', 'receivingYardsAfterCatch',
                      'receivingYardsPerGame', 'receptions', 'totalPointsPerGame', 'totalTouchdowns', 'totalYards', 'yardsPerGame', 'yardsPerReception']
        for i in stats:
          name = i['name']
          full_stat_name = cat+'_'+name
          if name in stat_names:
            espn_data['espn'][full_stat_name] = i['value']
    players_data.append(espn_data)
  return players_data

def espn_odds_parser(p1_team, p2_team, p1_url, p2_url):
  p1_data = requests.get(p1_url).json()['items']
  p2_data = requests.get(p2_url).json()['items']
  p1_odds_data = p1_data[0][p1_team[1]+'TeamOdds']
  p2_odds_data = p2_data[0][p2_team[1]+'TeamOdds']
  p1_team_data = {'favorite': p1_odds_data['favorite'], 'spread_odds': p1_odds_data['current']['moneyLine']['alternateDisplayValue']}
  p2_team_data = {'favorite': p2_odds_data['favorite'], 'spread_odds': p2_odds_data['current']['moneyLine']['alternateDisplayValue']}
  teams_data = [p1_team_data, p2_team_data]
  return teams_data

# def predictions_parser(p1_team, p2_team, p1_url, p2_url):
#   p1_data = requests.get(p1_url)
#   p2_data = requests.get(p2_url)
#   ipdb.set_trace()

def espn_players_compare(player1, player2, player1_name, player2_name):
  p1 = player1[2]['espn']
  p2 = player2[2]['espn']
  compared_hash = {}
  for key, value in p1.items():
    if key == 'General_fumbles':
      winner = player1_name if value < p2[key] else player2_name
    else:
      winner = player1_name if value > p2[key] else player2_name
    compared_hash[key] = winner
  return compared_hash

def compare_players(player1, player2, week):
  split_player1 = player1.split('_')
  split_player2 = player2.split('_')
  player1_fullname = ' '.join(split_player1)
  player2_fullname = ' '.join(split_player2)
  player1_list = []
  player2_list = []
  api_urls = {
  'tank':       "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerInfo",
  'matchups':   "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLGamesForWeek",
  'espn_stats': "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/athletes/pid/statistics/0?lang=en&region=us",
  'espn_odds':  "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/event_id/competitions/event_id/odds"
  # 'predictions': "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/event_id/competitions/event_id/odds",
  }
  tank_api_key = os.getenv('TANK_KEY')
  tank_api_host = os.getenv('TANK_HOST')
  # with alive_bar(3) as bar:
  for key, value in api_urls.items():
    url = value
    match key:
      case 'tank':
        player1_params = {'playerName': player1, 'getStats': 'true'}
        player2_params = {'playerName': player2, 'getStats': 'true'}
        headers = {"X-RapidAPI-Key": tank_api_key, "X-RapidAPI-Host": tank_api_host}
        tank_data = tank_parser(url, headers, player1_params, player2_params)
        player1_list.append(tank_data[0])
        player2_list.append(tank_data[1])
      # bar()
      case 'matchups':
        # year = str(datetime.date.today().year)
        query_params = {'week': week, 'seasonType': 'reg', 'season': '2023'}
        headers = {"X-RapidAPI-Key": tank_api_key, "X-RapidAPI-Host": tank_api_host}
        teams = [player1_list[0]['tank']['team'], player2_list[0]['tank']['team']]
        matchups_data = matchups_parser(url, headers, query_params, teams)
        player1_list.append({'matchups': matchups_data[0]})
        player2_list.append({'matchups': matchups_data[1]})
      case 'espn_stats':
        p1_pos = player1_list[0]['tank']['position']
        p2_pos = player2_list[0]['tank']['position']
        p1_espn_id = player1_list[0]['tank']['espn_id']
        p2_espn_id = player2_list[0]['tank']['espn_id']
        espn_data = espn_parser(url, p1_espn_id, p2_espn_id, p1_pos, p2_pos)
        player1_list.append(espn_data[0])
        player2_list.append(espn_data[1])
      # bar()
      case 'espn_odds':
        p1_team = [player1_list[0]['tank']['team'], player1_list[1]['matchups']['home_or_away']]
        p2_team = [player2_list[0]['tank']['team'], player2_list[1]['matchups']['home_or_away']]
        p1_event_id = player1_list[1]['matchups']['espnID']
        p2_event_id = player2_list[1]['matchups']['espnID']
        split_url = url.split('event_id')
        p1_url = split_url[0]+p1_event_id+split_url[1]+p1_event_id+split_url[2]
        p2_url = split_url[0]+p2_event_id+split_url[1]+p2_event_id+split_url[2]
        odds_data = espn_odds_parser(p1_team, p2_team, p1_url, p2_url)
        player1_list.append({'odds': odds_data[0]})
        player2_list.append({'odds': odds_data[1]})
      # maybe not with predictions
      # case 'predictions':
      #   p1_team = player1_list[0]['tank']['team']
      #   p2_team = player2_list[0]['tank']['team']
      #   p1_event_id = player1_list[1]['matchups']['espnID']
      #   p2_event_id = player2_list[1]['matchups']['espnID']
      #   split_url = url.split('event_id')
      #   p1_url = split_url[0]+p1_event_id+split_url[1]+p1_event_id+split_url[2]
      #   p2_url = split_url[0]+p2_event_id+split_url[1]+p2_event_id+split_url[2]
      #   predictions_data = predictions_parser(p1_team, p2_team, p1_url, p2_url)
        
  ipdb.set_trace()
  espn_compare_dict = espn_players_compare(player1_list, player2_list, player1_fullname, player2_fullname)
  p1_list = []
  p2_list = []
  for key, value in espn_compare_dict.items():
    if value == player1_fullname:
      p1_list.append(value)
    else:
      p2_list.append(value)
  p1_list_len = len(p1_list)
  p2_list_len = len(p2_list)
  print(player1_fullname+' total points: '+str(p1_list_len))
  print('----------')
  print(player2_fullname+' total points: '+str(p2_list_len))
  print('-----------')
  winner = player1_fullname if p1_list_len > p2_list_len else player2_fullname
  print('winner is ' + winner)
  # bar()
  # print('----------------')
  # print(player1_fullname)  
  # pprint.pprint(player1_list)
  # print('-----------------------------')
  # print(player2_fullname)
  # pprint.pprint(player2_list)

def main():
  player1 = sys.argv[1]
  player2 = sys.argv[2]
  week = sys.argv[3]
  compare_players(player1, player2, week)
    

if __name__ == "__main__":
  main()