# test_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/nfl_stats.db")
conn = sqlite3.connect(DB_PATH)

# Check what we have
cursor = conn.execute("SELECT COUNT(*) FROM players")
print(f"Players: {cursor.fetchone()[0]}")

cursor = conn.execute("SELECT COUNT(*) FROM player_stats")
print(f"Stat records: {cursor.fetchone()[0]}")

# Check what columns actually exist in players table
cursor = conn.execute("PRAGMA table_info(players)")
print("\nPlayers table columns:")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

# Sample query - FIXED
cursor = conn.execute("""
    SELECT p.player_name, p.position, p.recent_team, s.season, s.week, s.passing_yards
    FROM player_stats s
    JOIN players p ON s.player_id = p.player_id
    WHERE p.player_name LIKE '%Mahomes%'
    AND s.season = 2024
    ORDER BY s.week
    LIMIT 5
""")

print("\nSample - Mahomes 2024:")
for row in cursor.fetchall():
    print(f"  Week {row[4]}: {row[5]} passing yards")

conn.close()