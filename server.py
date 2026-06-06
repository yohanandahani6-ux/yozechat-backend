import os
import asyncio
import websockets
import json
import sqlite3
from datetime import datetime

# Keep track of all active group members
CONNECTED_ROOM = set()

# 💾 Step 1: Initialize SQLite Database
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
        # Step 1: Safe Handshake protocol with a short timeout
        try:
            # Wait up to 2 seconds for the app to send its username string
            username = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        except asyncio.TimeoutError:
            # If the app didn't send a name instantly, use a fallback
            username = f"User_{id(websocket) % 1000}"
            
        join_alert = f"📢 [SYSTEM]: {username} has entered the group chat room!"
        print(join_alert)
        
        # Broadcast entry to everyone
        for client in CONNECTED_ROOM:
            try:
                await client.send(join_alert)
            except Exception:
                pass

        # Step 2: Continuous loop to stream incoming text blocks
        async for message in websocket:
            try:
                # Check if incoming data is a structural JSON action (like fetch_history)
                payload = json.loads(message)
                action = payload.get("action")
                
                if action == "fetch_history":
                    # Read history from database file
                    conn = sqlite3.connect("chat_history.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender, message, timestamp FROM messages ORDER BY id ASC")
                    rows = cursor.fetchall()
                    conn.close()
                    
                    history_payload = {
                        "type": "history",
                        "messages": [{"sender": r[0], "message": r[1], "timestamp": r[2]} for r in rows]
                    }
                    # Send database history ONLY back to this requesting client
                    await websocket.send(json.dumps(history_payload))
                    continue # Skip broadcasting this management command
                    
            except json.JSONDecodeError:
                # If it's a raw text string, proceed with standard message relay logic
                pass

            # 💾 Save incoming afternoon chats to history database file
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect("chat_history.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)",
                (username, message, timestamp)
            )
            conn.commit()
            conn.close()

            # Format real-time terminal and network payloads
            formatted_payload = f"{username}: {message}"
            print(f"[Group Log] {formatted_payload}")
            
            # Relay out to all windows instantly
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
    init_db() # Run database verification checks
    
    # 🌐 CLOUD CONFIGURATION: Pull the platform runtime environment variable
    # Defaults to 8765 if you run it locally on your machine
    port = int(os.environ.get("PORT", 8765))
    
    print("=======================================")
    print("      YOZECHAT 3-WAY NETWORK ROUTER     ")
    print("=======================================")
    print(f"Listening for group windows on port {port}...")

    # Bind to 0.0.0.0 to accept traffic from external public networks
    async with websockets.serve(
        chat_handler, 
        "0.0.0.0", 
        port, 
        ping_interval=10, 
        ping_timeout=10
    ):
        await asyncio.Future() # Keep server thread alive infinitely

if __name__ == "__main__":
    asyncio.run(main())