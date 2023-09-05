# pry tool:  ipdb.set_trace()

import requests
import sys
import ipdb
import os
import json
import pprint

APIS = {
  'tank': "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerInfo"
}

def tank_parser(player1_request, player2_request):
  ipdb.set_trace()

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
    player1_request = {'url': url, 'headers': headers, 'params': player1_params}
    player2_request = {'url': url, 'headers': headers, 'params': player2_params} #requests.get(url, headers=headers, params=player2_params).json()['body'][0]
    if value == 'tank':
      tank_parser(player1_request, player2_request)
      # here will be espn

    # ipdb.set_trace()
    # match value:
    #   case 'tank':
    #     tank_parser(player1_response, player2_response)
    # player1_list.append(player1_json)
    # player2_list.append(player2_json)
    # pprint.pprint(player1_list)
    # pprint.pprint(player2_list)

def main():
  player1 = sys.argv[1]
  player2 = sys.argv[2]
  compare_players(player1, player2)
    

if __name__ == "__main__":
  main()