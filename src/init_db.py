# src/init_db.py - NEW FILE
import sqlite3
from pathlib import Path

DB_PATH = Path("data/nfl_stats.db")

def init_db():
    """Initialize database with proper schema"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Drop old tables if they exist
    conn.execute("DROP TABLE IF EXISTS player_stats")
    conn.execute("DROP TABLE IF EXISTS players")
    
    # Create players table with BOTH name fields
    conn.execute("""
        CREATE TABLE players (
            player_id TEXT PRIMARY KEY,
            player_name TEXT,
            player_display_name TEXT,
            position TEXT,
            recent_team TEXT,
            sportradar_id TEXT,
            headshot_url TEXT
        )
    """)
    
    # Create player_stats table
    conn.execute("""
        CREATE TABLE player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT,
            season INTEGER,
            week INTEGER,
            passing_yards REAL,
            passing_tds INTEGER,
            interceptions INTEGER,
            completions INTEGER,
            attempts INTEGER,
            rushing_yards REAL,
            rushing_tds INTEGER,
            carries INTEGER,
            receiving_yards REAL,
            receiving_tds INTEGER,
            receptions INTEGER,
            targets INTEGER,
            offensive_snaps INTEGER,
            offensive_snap_pct REAL,
            fanduel_fantasy_points REAL,
            avg_fppg REAL,
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            UNIQUE(player_id, season, week)
        )
    """)
    
    # Create indexes for faster queries
    conn.execute("CREATE INDEX idx_player_display_name ON players(player_display_name)")
    conn.execute("CREATE INDEX idx_player_stats_lookup ON player_stats(player_id, season, week)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database schema initialized at: {DB_PATH.absolute()}")

if __name__ == "__main__":
    init_db()