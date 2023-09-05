# pry tool
# import ipdb; ipdb.set_trace()

APIS = {
  
}

import sys

def compare_teams(team1, team2):
  split_team1 = team1.split('_')
  split_team2 = team2.split('_')
  team1_city = split_team1[0]
  team1_name = split_team1[1]
  team2_city = split_team2[0]
  team2_name = split_team2[1]
  team1_fullname = ' '.join(split_team1)
  team2_fullname = ' '.join(split_team2)
  print(team1_fullname + " vs " + team2_fullname)
  
def main():
  team1 = sys.argv[1]
  team2 = sys.argv[2]
  compare_teams(team1, team2)
  
if __name__ == "__main__":
  main()