# src/server.py - UPDATED TO USE FULL NAMES
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
import sqlite3
from pathlib import Path

DB_PATH = Path("data/nfl_stats.db")

def init_db():
    """Database is already created by data_collector.py"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run data_collector.py first.")

app = Server("nfl-stats-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_player_stats",
            description="Get NFL player statistics for a specific season/week. Supports full names like 'Patrick Mahomes' or 'Josh Allen'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "Player's full name (e.g., 'Patrick Mahomes', 'Josh Allen')"
                    },
                    "season": {
                        "type": "integer",
                        "description": "NFL season year (e.g., 2024)"
                    },
                    "week": {
                        "type": "integer",
                        "description": "Week number (1-18) or -1 for season average",
                    }
                },
                "required": ["player_name", "season"]
            }
        ),
        Tool(
            name="compare_players",
            description="Compare two players' season stats side-by-side. Use full names.",
            inputSchema={
                "type": "object",
                "properties": {
                    "player1": {"type": "string", "description": "First player's full name"},
                    "player2": {"type": "string", "description": "Second player's full name"},
                    "season": {"type": "integer"}
                },
                "required": ["player1", "player2", "season"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_player_stats":
        return await get_player_stats(
            arguments["player_name"],
            arguments["season"],
            arguments.get("week")
        )
    elif name == "compare_players":
        return await compare_players(
            arguments["player1"],
            arguments["player2"],
            arguments["season"]
        )

async def get_player_stats(player_name: str, season: int, week: int = None):
    conn = sqlite3.connect(DB_PATH)
    
    # UPDATED: Search by player_display_name
    query = """
        SELECT p.player_display_name, p.position, p.recent_team,
               s.season, s.week, 
               s.passing_yards, s.passing_tds, s.interceptions,
               s.rushing_yards, s.rushing_tds, s.carries,
               s.receiving_yards, s.receiving_tds, s.receptions, s.targets
        FROM player_stats s
        JOIN players p ON s.player_id = p.player_id
        WHERE p.player_display_name LIKE ? AND s.season = ?
    """
    params = [f"%{player_name}%", season]
    
    if week is not None:
        query += " AND s.week = ?"
        params.append(week)
    
    query += " ORDER BY s.week"
    
    cursor = conn.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return [TextContent(
            type="text", 
            text=f"No stats found for '{player_name}' in {season}"
        )]
    
    # Format response
    name, pos, team = results[0][0], results[0][1], results[0][2]
    response = f"📊 {name} ({pos} - {team}) - {season} Season\n\n"
    
    for row in results:
        week_num = row[4]
        week_label = "Season Avg" if week_num == -1 else f"Week {week_num}"
        
        response += f"{week_label}:\n"
        if row[5] and row[5] > 0:  # passing_yards
            response += f"  Pass: {row[5]:.0f} yds, {row[6]} TDs, {row[7]} INTs\n"
        if row[8] and row[8] > 0:  # rushing_yards
            response += f"  Rush: {row[8]:.0f} yds, {row[9]} TDs ({row[10]} carries)\n"
        if row[11] and row[11] > 0:  # receiving_yards
            response += f"  Rec: {row[11]:.0f} yds, {row[12]} TDs ({row[13]}/{row[14]} targets)\n"
        response += "\n"
    
    return [TextContent(type="text", text=response)]

async def compare_players(player1: str, player2: str, season: int):
    conn = sqlite3.connect(DB_PATH)
    
    # UPDATED: Search by player_display_name
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
    
    cursor = conn.execute(query, [f"%{player1}%", season])
    p1_stats = cursor.fetchone()
    
    cursor = conn.execute(query, [f"%{player2}%", season])
    p2_stats = cursor.fetchone()
    
    conn.close()
    
    if not p1_stats or not p2_stats:
        return [TextContent(
            type="text",
            text=f"Could not find stats for both players in {season}"
        )]
    
    response = f"⚖️  Player Comparison - {season}\n\n"
    response += f"{p1_stats[0]} ({p1_stats[1]}) vs {p2_stats[0]} ({p2_stats[1]})\n\n"
    
    if p1_stats[2] or p2_stats[2]:  # passing
        response += "Passing:\n"
        response += f"  {p1_stats[0]}: {p1_stats[2]:.0f} yds, {p1_stats[3]} TDs\n"
        response += f"  {p2_stats[0]}: {p2_stats[2]:.0f} yds, {p2_stats[3]} TDs\n\n"
    
    if p1_stats[4] or p2_stats[4]:  # rushing
        response += "Rushing:\n"
        response += f"  {p1_stats[0]}: {p1_stats[4]:.0f} yds, {p1_stats[5]} TDs\n"
        response += f"  {p2_stats[0]}: {p2_stats[4]:.0f} yds, {p2_stats[5]} TDs\n\n"
    
    if p1_stats[6] or p2_stats[6]:  # receiving
        response += "Receiving:\n"
        response += f"  {p1_stats[0]}: {p1_stats[6]:.0f} yds, {p1_stats[7]} TDs\n"
        response += f"  {p2_stats[0]}: {p2_stats[6]:.0f} yds, {p2_stats[7]} TDs\n"
    
    return [TextContent(type="text", text=response)]

if __name__ == "__main__":
    init_db()
    mcp.server.stdio.stdio_server()(app)