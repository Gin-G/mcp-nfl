# src/data_collector.py
import sqlite3
import pandas as pd
import nflreadpy as nfl
from pathlib import Path

DB_PATH = Path("data/nfl_stats.db")

def collect_and_store(seasons=[2024, 2025]):
    """Run your data collection and store in DB"""
    
    # CREATE THE DIRECTORY FIRST
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Collecting NFL data for seasons: {seasons}")
    
    # Load data from nflreadpy
    player_stats = nfl.load_player_stats(seasons=seasons).to_pandas()
    
    print(f"Loaded {len(player_stats)} player-game records")
    
    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    
    # Store BOTH player_name and player_display_name
    player_columns = ['player_id', 'player_name', 'player_display_name', 'position']
    
    # Handle team column
    if 'recent_team' in player_stats.columns:
        player_columns.append('recent_team')
    elif 'team' in player_stats.columns:
        player_stats['recent_team'] = player_stats['team']
        player_columns.append('recent_team')
    
    # Add optional columns
    if 'sportradar_id' in player_stats.columns:
        player_columns.append('sportradar_id')
    if 'headshot_url' in player_stats.columns:
        player_columns.append('headshot_url')
    
    players = player_stats[player_columns].drop_duplicates('player_id')
    
    # Add missing columns as NULL if needed
    for col in ['sportradar_id', 'headshot_url']:
        if col not in players.columns:
            players[col] = None
    
    players.to_sql('players', conn, if_exists='replace', index=False)
    
    print(f"Stored {len(players)} unique players")
    
    # Store stats
    stats = player_stats.copy()
    
    # Handle week column
    if 'week' in stats.columns:
        stats['week'] = pd.to_numeric(stats['week'], errors='coerce').fillna(-1).astype(int)
    
    # Map columns
    stat_columns = {
        'player_id': 'player_id',
        'season': 'season', 
        'week': 'week',
        'passing_yards': 'passing_yards',
        'passing_tds': 'passing_tds',
        'interceptions': 'passing_interceptions',  # Note: source column name
        'completions': 'completions',
        'attempts': 'attempts',
        'rushing_yards': 'rushing_yards',
        'rushing_tds': 'rushing_tds',
        'carries': 'carries',
        'receiving_yards': 'receiving_yards',
        'receiving_tds': 'receiving_tds',
        'receptions': 'receptions',
        'targets': 'targets'
    }
    
    # Build stats dataframe
    stats_to_store = pd.DataFrame()
    for db_col, source_col in stat_columns.items():
        if source_col in stats.columns:
            stats_to_store[db_col] = stats[source_col]
        else:
            stats_to_store[db_col] = 0
    
    # Add nullable columns
    for col in ['offensive_snaps', 'offensive_snap_pct', 'fanduel_fantasy_points', 'avg_fppg']:
        if col in stats.columns:
            stats_to_store[col] = stats[col]
        else:
            stats_to_store[col] = None
    
    stats_to_store.to_sql('player_stats', conn, if_exists='replace', index=False)
    
    print(f"Stored {len(stats_to_store)} stat records")
    
    conn.close()
    print(f"✅ Database created at: {DB_PATH.absolute()}")

if __name__ == "__main__":
    collect_and_store()