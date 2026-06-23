


import os
import asyncio
import websockets
import json
import sqlite3
from datetime import datetime, timezone # 👈 Added timezone here

# Keep track of all active group members
CONNECTED_ROOM = set()

# ... (init_db remains exactly as it was)
def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

async def chat_handler(websocket):
    CONNECTED_ROOM.add(websocket)
    username = "Guest Phone"
    
    try:
        try:
            username = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        except asyncio.TimeoutError:
            username = f"User_{id(websocket) % 1000}"
            
        join_alert = f"📢 [SYSTEM]: {username} has entered the group chat room!"
        print(join_alert)
        
        for client in CONNECTED_ROOM:
            try:
                await client.send(join_alert)
            except Exception:
                pass

        async for message in websocket:
            try:
                payload = json.loads(message)
                action = payload.get("action")
                
                if action == "fetch_history":
                    conn = sqlite3.connect("chat_history.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender, message, timestamp FROM messages ORDER BY id ASC")
                    rows = cursor.fetchall()
                    conn.close()
                    
                    history_payload = {
                        "type": "history",
                        "messages": [{"sender": r[0], "message": r[1], "timestamp": r[2]} for r in rows]
                    }
                    await websocket.send(json.dumps(history_payload))
                    continue
                    
            except json.JSONDecodeError:
                pass

            # 💾 UPDATED: Save using UTC to standardize time across all regions
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            
            conn = sqlite3.connect("chat_history.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)",
                (username, message, timestamp)
            )
            conn.commit()
            conn.close()

            formatted_payload = f"{username}: {message}"
            print(f"[Group Log] {formatted_payload}")
            
            for client in CONNECTED_ROOM:
                try:
                    await client.send(formatted_payload)
                except Exception:
                    pass
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in CONNECTED_ROOM:
            CONNECTED_ROOM.remove(websocket)
        exit_alert = f"❌ [SYSTEM]: {username} has disconnected from the room."
        print(exit_alert)
        for client in CONNECTED_ROOM:
            try:
                await client.send(exit_alert)
            except Exception:
                pass

async def main():
    init_db()
    port = int(os.environ.get("PORT", 8765))
    print("=======================================")
    print("      YOZECHAT 3-WAY NETWORK ROUTER     ")
    print("=======================================")
    print(f"Listening for group windows on port {port}...")

    async with websockets.serve(
        chat_handler, 
        "0.0.0.0", 
        port, 
        ping_interval=10, 
        ping_timeout=10
    ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())