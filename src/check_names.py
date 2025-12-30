# check_display_names.py
import sqlite3
from pathlib import Path
import nflreadpy as nfl

DB_PATH = Path("data/nfl_stats.db")

# Check what nflreadpy actually provides
print("Checking nflreadpy data columns:")
print("="*80)

sample = nfl.load_player_stats(seasons=[2024]).to_pandas()

# Show available columns
print(f"Available columns: {list(sample.columns)[:20]}")

# Check a specific player
allen = sample[sample['player_name'].str.contains('Allen', case=False, na=False) & 
               (sample['position'] == 'QB')].head(1)

if not allen.empty:
    player = allen.iloc[0]
    print("\nJosh Allen example:")
    print(f"  player_name: {player.get('player_name', 'N/A')}")
    print(f"  player_display_name: {player.get('player_display_name', 'N/A')}")
    print(f"  player_id: {player.get('player_id', 'N/A')}")

# Check Lamar Jackson
jackson = sample[sample['player_name'].str.contains('Jackson', case=False, na=False) & 
                 (sample['position'] == 'QB')].head(1)

if not jackson.empty:
    player = jackson.iloc[0]
    print("\nLamar Jackson example:")
    print(f"  player_name: {player.get('player_name', 'N/A')}")
    print(f"  player_display_name: {player.get('player_display_name', 'N/A')}")
    print(f"  player_id: {player.get('player_id', 'N/A')}")

# Check Mahomes
mahomes = sample[sample['player_name'].str.contains('Mahomes', case=False, na=False)].head(1)

if not mahomes.empty:
    player = mahomes.iloc[0]
    print("\nPatrick Mahomes example:")
    print(f"  player_name: {player.get('player_name', 'N/A')}")
    print(f"  player_display_name: {player.get('player_display_name', 'N/A')}")
    print(f"  player_id: {player.get('player_id', 'N/A')}")