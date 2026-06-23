# YozeChat Secured Cloud Router

An asynchronous, highly concurrent WebSocket chat router built with Python, optimized for live deployment on the **Railway Cloud Platform**, and engineered to handle remote mobile client network links. 

This platform serves as a production-grade portfolio project designed for technical evaluation during the August 2026 Fieldwork attachment program in Kiteto District, Manyara Region.

---

## 🚀 Key Engineering Milestones

*   **Asynchronous Concurrency**: Built on top of Python’s `asyncio` and `websockets` architecture, enabling hundreds of parallel socket channels to stream simultaneously without resource blocking.
*   **Intelligent Thread Pooling (`run_in_executor`)**: Mitigates Python's synchronous file system blocks. Database operations interacting with the SQLite storage layer are delegated to background workers, ensuring zero lag on real-time network relays.
*   **Header-Based Fingerprint Filtering**: Implements proactive security checks at the initial HTTP Handshake level. Automated internet web scanners and malicious port crawlers are dropped instantly with a `401 Unauthorized` response before entering application memory space.
*   **Production Cloud Optimization**: Custom-tuned network arguments eliminate the common cloud reverse-proxy timeouts (30-60 second idle drops) and mitigate carrier-side DNS reverse lookup lag for instant client handshakes.

---

## 🛠️ System Architecture Flow

```text
  [ Mobile Client App ] ---> ( Handshake Header Check: X-YozeChat-Auth )
                                        |
                                        v
                          [ YozeChat Secured Core ]
                               /              \
                              v                v
         [ Async WebSocket Broadcast ]   [ Non-Blocking SQLite Worker ]
           (Relays out to all users)       (Appends chat history to disk)
```

---

## 📂 Codebase Overview (`server.py`)

The backend script handles three critical network layers:
1.  **Handshake Security**: Automatically monitors incoming client proxy headers (`X-Forwarded-For`) to track real client IP addresses, matching secrets against environment variables (`os.getenv`).
2.  **Protocol Switching**: Uses structure checks to identify and process system requests (like JSON-formatted history dumps via `fetch_history`) while safely handling standard string payloads without overhead.
3.  **Graceful Disconnection Lifecycles**: An async `finally` block guarantees that even if a mobile device drops connection due to weak tower signals, its session resources are purged immediately from the active routing map.

---

## ⚙️ Cloud Configuration (Railway Setup)

To keep your secret authorization token isolated from the public source code, the system relies on cloud-injected configuration values.

1. Navigate to your **Railway Project Dashboard**.
2. Select your active service container and click on the **Variables** tab.
3. Click **New Variable** and configure the key-value pair:
   * **Key**: `CHAT_SECRET_KEY`
   * **Value**: *YourSecureHandshakePassphrase*

---

## 📱 Integration Guide for Client Applications

When connecting your client application or desktop interface to this router, the connection pipeline must pass the security handshake token inside the HTTP upgrade headers:

```python
import asyncio
import websockets

async def connect_yoze_chat():
    # Production deployment routing url
    uri = "wss://your-project.up.railway.app"
    
    # Custom authorization header matching your server configuration
    headers = {
        "X-YozeChat-Auth": "KitetoSecure2026"
    }
    
    async with websockets.connect(uri, extra_headers=headers, ping_interval=20) as ws:
        # Immediately declare your identity to complete connection verification
        await ws.send("YourUsername")
        print("Secure pipeline verified with cloud router core.")
```

---

## 👨‍💻 Developer Profile

**Yohana Zebedayo Ndahani**  
*Software Developer & Telecommunications Engineer*

* **Institution:** University of Dar es Salaam (UDSM)
* **Academic Program:** Bachelor of Science in Telecommunications Engineering
* **Technical Focus:** High-Concurrency Network Engineering, Systems Architecture, & Cross-Platform Development
* **Core Competencies:** 
  * **Languages & Frameworks:** Python (AsyncIO, WebSockets), Java (Advanced OOP), Flutter (Mobile Deployment)
  * **Network & Security:** Subnetting, VLAN Configuration, OSI Model Architecture, & Fundamental Cybersecurity
  * **Hardware & Signals:** Digital Electronics (Sequential Logic), Signal Processing, & Antenna Parameters
* **Project Designation:** Developed as a production-grade portfolio asset for technical evaluation during the August 2026 Fieldwork Attachment Program .
