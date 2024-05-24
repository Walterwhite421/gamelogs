#hitter + pitcher stats previous 5 game logs  
 
import requests 

import pandas as pd 

from datetime import datetime, timedelta 

  

# Function to get the previous day's date in YYYY-MM-DD format 

def get_previous_date(): 

    yesterday = datetime.now() - timedelta(1) 

    return yesterday.strftime('%Y-%m-%d') 

  

# Function to fetch and process stats for all hitters and pitchers from the previous day 

def fetch_mlb_stats(): 

    previous_date = get_previous_date() 

    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={previous_date}" 

     

    response = requests.get(url) 

    if response.status_code != 200: 

        print(f"Failed to fetch data: {response.status_code}") 

        return pd.DataFrame(), pd.DataFrame() 

     

    games = response.json().get('dates', [])[0].get('games', []) 

    batting_stats = [] 

    pitching_stats = [] 

  

    for game in games: 

        game_id = game.get('gamePk') 

        boxscore_url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore" 

        boxscore_response = requests.get(boxscore_url) 

        if boxscore_response.status_code != 200: 

            continue 

  

        boxscore = boxscore_response.json() 

        for team in ['home', 'away']: 

            players = boxscore['teams'][team]['players'] 

            for player_id, player_info in players.items(): 

                batting = player_info['stats'].get('batting') 

                if batting: 

                    batting_stats.append({ 

                        'name': player_info['person']['fullName'], 

                        'team': boxscore['teams'][team]['team']['name'], 

                        'hits': batting.get('hits', 0), 

                        'atBats': batting.get('atBats', 0), 

                        'homeRuns': batting.get('homeRuns', 0), 

                        'strikeOuts': batting.get('strikeOuts', 0) 

                    }) 

                 

                pitching = player_info['stats'].get('pitching') 

                if pitching: 

                    pitching_stats.append({ 

                        'name': player_info['person']['fullName'], 

                        'team': boxscore['teams'][team]['team']['name'], 

                        'player_id': player_info['person']['id'], 

                        'hitsAllowed': pitching.get('hits', 0), 

                        'runsAllowed': pitching.get('runs', 0), 

                        'homeRunsAllowed': pitching.get('homeRuns', 0), 

                        'walks': pitching.get('baseOnBalls', 0), 

                        'strikeOuts': pitching.get('strikeOuts', 0), 

                        'outs': pitching.get('outs', 0), 

                        'inningsPitched': pitching.get('inningsPitched', 0) 

                    }) 

  

    if not batting_stats: 

        print("No hitting stats found for the previous day.") 

    if not pitching_stats: 

        print("No pitching stats found for the previous day.") 

     

    # Convert to DataFrame for better readability 

    batting_df = pd.DataFrame(batting_stats) 

    pitching_df = pd.DataFrame(pitching_stats) 

  

    return batting_df, pitching_df 

  

# Function to fetch recent game logs for a pitcher 

def fetch_recent_games_stats(player_id): 

    recent_games_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats/game" 

    params = { 

        "stats": "gameLog", 

        "group": "pitching", 

        "gameType": "R", 

        "leagueListId": "mlb_milb_aaa", 

        "limit": 5 

    } 

    response = requests.get(recent_games_url, params=params) 

    if response.status_code != 200: 

        print(f"Failed to fetch recent games data: {response.status_code}") 

        return pd.DataFrame() 

     

    recent_games = response.json().get('stats', [])[0].get('splits', []) 

    if not recent_games: 

        print(f"No recent games data found for player with ID: {player_id}") 

        return pd.DataFrame() 

     

    game_stats = [] 

    for game in recent_games: 

        game_data = game.get('stat', {}) 

        game_stats.append({ 

            'date': game['date'], 

            'team': game['team']['name'], 

            'hitsAllowed': game_data.get('hits', 0), 

            'runsAllowed': game_data.get('runs', 0), 

            'homeRunsAllowed': game_data.get('homeRuns', 0), 

            'walks': game_data.get('baseOnBalls', 0), 

            'strikeOuts': game_data.get('strikeOuts', 0), 

            'outs': game_data.get('outs', 0), 

            'inningsPitched': game_data.get('inningsPitched', 0) 

        }) 

  

    return pd.DataFrame(game_stats) 

  

# Fetch the stats in the background 

batting_stats_df, pitching_stats_df = fetch_mlb_stats() 

  

# Function to search and display stats for a player 

def search_player_stats(player_name, batting_df, pitching_df): 

    batting_stats = batting_df[batting_df['name'].str.contains(player_name, case=False, na=False)] 

    pitching_stats = pitching_df[pitching_df['name'].str.contains(player_name, case=False, na=False)] 

  

    if batting_stats.empty and pitching_stats.empty: 

        print(f"No stats found for player: {player_name}") 

    else: 

        if not batting_stats.empty: 

            print("Batting Stats:") 

            print(batting_stats) 

        if not pitching_stats.empty: 

            print("Pitching Stats:") 

            print(pitching_stats) 

             

            # Fetch recent games stats for pitchers 

            player_id = pitching_stats['player_id'].values[0] 

            recent_games_stats = fetch_recent_games_stats(player_id) 

            if not recent_games_stats.empty: 

                print("Recent Games Stats:") 

                print(recent_games_stats) 

  

# Prompt the user to enter a player's name and search for their stats 

while True: 

    player_name = input("Which player are you searching for? (type 'exit' to quit): ") 

    if player_name.lower() == 'exit': 

        break 

    search_player_stats(player_name, batting_stats_df, pitching_stats_df) 
