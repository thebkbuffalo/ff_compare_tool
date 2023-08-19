# pry tool
# import ipdb; ipdb.set_trace()

import sys

PLAYER_APIS = []
TEAM_APIS = []
BOTH_APIS = []

def compare_players(player1, player2):
  split_player1 = player1.split('_')
  split_player2 = player2.split('_')
  player1_fullname = ' '.join(split_player1)
  player2_fullname = ' '.join(split_player2)
  print(player1_fullname + " vs " + player2_fullname)

def main():
  player1 = sys.argv[1]
  player2 = sys.argv[2]
  compare_players(player1, player2)
    

if __name__ == "__main__":
  main()