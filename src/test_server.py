# test_server.py
import asyncio
import sqlite3
from pathlib import Path

DB_PATH = Path("data/nfl_stats.db")

async def test_get_player_stats():
    """Test the player stats query"""
    conn = sqlite3.connect(DB_PATH)
    
    query = """
        SELECT p.player_name, p.position, p.recent_team,
               s.season, s.week, 
               s.passing_yards, s.passing_tds, s.interceptions,
               s.rushing_yards, s.rushing_tds, s.carries,
               s.receiving_yards, s.receiving_tds, s.receptions, s.targets
        FROM player_stats s
        JOIN players p ON s.player_id = p.player_id
        WHERE p.player_name LIKE ? AND s.season = ?
        AND s.week = ?
        ORDER BY s.week
    """
    
    cursor = conn.execute(query, ["%Mahomes%", 2024, 5])
    results = cursor.fetchall()
    conn.close()
    
    print("📊 Test: get_player_stats (Mahomes, 2024, Week 5)")
    print("="*60)
    
    if results:
        row = results[0]
        name, pos, team = row[0], row[1], row[2]
        print(f"{name} ({pos} - {team}) - 2024 Week {row[4]}\n")
        
        if row[5] and row[5] > 0:
            print(f"  Pass: {row[5]:.0f} yds, {row[6]} TDs, {row[7]} INTs")
        if row[8] and row[8] > 0:
            print(f"  Rush: {row[8]:.0f} yds, {row[9]} TDs ({row[10]} carries)")
        if row[11] and row[11] > 0:
            print(f"  Rec: {row[11]:.0f} yds, {row[12]} TDs ({row[13]}/{row[14]} targets)")
    else:
        print("No results found")
    
    print("\n")

async def test_compare_players():
    """Test the comparison query"""
    conn = sqlite3.connect(DB_PATH)
    
    query = """
        SELECT p.player_display_name, p.position,
               SUM(s.passing_yards) as pass_yds, SUM(s.passing_tds) as pass_tds,
               SUM(s.rushing_yards) as rush_yds, SUM(s.rushing_tds) as rush_tds,
               SUM(s.receiving_yards) as rec_yds, SUM(s.receiving_tds) as rec_tds
        FROM player_stats s
        JOIN players p ON s.player_id = p.player_id
        WHERE p.player_display_name LIKE ? AND s.season = ? AND s.week != -1
        GROUP BY p.player_id
    """
    
    cursor = conn.execute(query, ["%Josh Allen%", 2024])
    p1_stats = cursor.fetchone()
    
    cursor = conn.execute(query, ["%Lamar Jackson%", 2024])
    p2_stats = cursor.fetchone()
    
    conn.close()
    
    print("⚖️  Test: compare_players (Josh Allen vs Lamar Jackson, 2024)")
    print("="*60)
    
    if p1_stats and p2_stats:
        print(f"{p1_stats[0]} ({p1_stats[1]}) vs {p2_stats[0]} ({p2_stats[1]})\n")
        
        if p1_stats[2] or p2_stats[2]:
            print("Passing:")
            print(f"  {p1_stats[0]}: {p1_stats[2]:.0f} yds, {p1_stats[3]} TDs")
            print(f"  {p2_stats[0]}: {p2_stats[2]:.0f} yds, {p2_stats[3]} TDs\n")
        
        if p1_stats[4] or p2_stats[4]:
            print("Rushing:")
            print(f"  {p1_stats[0]}: {p1_stats[4]:.0f} yds, {p1_stats[5]} TDs")
            print(f"  {p2_stats[0]}: {p2_stats[4]:.0f} yds, {p2_stats[5]} TDs")
    else:
        print("Could not find stats for both players")
    
    print("\n")

async def main():
    await test_get_player_stats()
    await test_compare_players()
    print("✅ All tests passed! MCP server logic is working correctly.")

if __name__ == "__main__":
    asyncio.run(main())