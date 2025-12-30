# quick_check.py - UPDATED
import sqlite3
from pathlib import Path

DB_PATH = Path("data/nfl_stats.db")
conn = sqlite3.connect(DB_PATH)

# Find Josh Allen and Lamar Jackson using FULL NAMES
print("Searching for 'Allen' (full names):")
cursor = conn.execute("""
    SELECT DISTINCT player_name, player_display_name 
    FROM players 
    WHERE player_display_name LIKE '%Allen%' AND position = 'QB' 
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  {row[0]:15} -> {row[1]}")

print("\nSearching for 'Jackson' (full names):")
cursor = conn.execute("""
    SELECT DISTINCT player_name, player_display_name 
    FROM players 
    WHERE player_display_name LIKE '%Jackson%' AND position = 'QB' 
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  {row[0]:15} -> {row[1]}")

# Verify the specific players we want
print("\nVerifying specific players:")
cursor = conn.execute("""
    SELECT player_name, player_display_name, position, recent_team
    FROM players 
    WHERE player_display_name IN ('Josh Allen', 'Lamar Jackson', 'Patrick Mahomes')
""")
for row in cursor.fetchall():
    print(f"  {row[1]:20} ({row[0]:10}) - {row[2]:3} - {row[3]}")

conn.close()