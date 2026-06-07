import os
import asyncio
import websockets
import json
import sqlite3
from datetime import datetime

# Keep track of all active group members
CONNECTED_ROOM = set()

# 🔑 SECURITY: Define an Access Token (Set this in Railway's Variables tab or keep fallback)
SECRET_TOKEN = os.getenv("CHAT_SECRET_KEY", "KitetoSecure2026")

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

# ⚡ Helper function to run database operations safely in a separate thread
def db_execute(query, params=(), fetch=False):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = None
    if fetch:
        data = cursor.fetchall()
    else:
        conn.commit()
    conn.close()
    return data

async def chat_handler(websocket):
    # 🔒 1. HEADER-BASED SECURITY CHECK (Blocks real scanners instantly)
    headers = websocket.request_headers
    client_ip = headers.get("X-Forwarded-For", websocket.remote_address)
    client_token = headers.get("X-YozeChat-Auth")
    
    if client_token != SECRET_TOKEN:
        print(f"[BLOCKED] Unauthorized bot/scanner dropped from IP: {client_ip}")
        return websockets.Response(status=401, text="Unauthorized Access")

    CONNECTED_ROOM.add(websocket)
    username = "Guest Phone"
    
    try:
        # Step 1: Safe Handshake protocol with a short timeout
        try:
            username = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        except asyncio.TimeoutError:
            username = f"User_{id(websocket) % 1000}"
            
        join_alert = f"📢 [SYSTEM]: {username} has entered the room! (IP: {client_ip})"
        print(join_alert)
        
        for client in CONNECTED_ROOM:
            try:
                await client.send(join_alert)
            except Exception:
                pass

        # Step 2: Continuous loop to stream incoming text blocks
        async for message in websocket:
            try:
                payload = json.loads(message)
                action = payload.get("action")
                
                if action == "fetch_history":
                    # Non-blocking async call to read database history
                    loop = asyncio.get_running_loop()
                    rows = await loop.run_in_executor(
                        None, db_execute, "SELECT sender, message, timestamp FROM messages ORDER BY id ASC", (), True
                    )
                    
                    history_payload = {
                        "type": "history",
                        "messages": [{"sender": r[0], "message": r[1], "timestamp": r[2]} for r in rows]
                    }
                    await websocket.send(json.dumps(history_payload))
                    continue 
                    
            except json.JSONDecodeError:
                pass

            # 💾 Non-blocking async write to SQLite database
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, 
                db_execute, 
                "INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)", 
                (username, message, timestamp)
            )

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
    print("      YOZECHAT SECURED CLOUD ROUTER    ")
    print("=======================================")
    print(f"Listening for verified windows on port {port}...")

    # 🌐 OPTIMIZED CLOUD DEPLOYMENT SETTINGS
    async with websockets.serve(
        chat_handler, 
        "0.0.0.0", 
        port, 
        ping_interval=20,     # Keeps the connection alive through Railway's reverse proxy
        ping_timeout=20,      # Prevents timeout drops during silent/idle periods
        process_request=None  # Disables automatic DNS resolution to remove the 1-minute handshake lag
    ):
        await asyncio.Future() 

if __name__ == "__main__":
    asyncio.run(main())
