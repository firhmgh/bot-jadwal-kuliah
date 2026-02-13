from flask import Flask
from threading import Thread
import os

app = Flask('')

# --- HTML & CSS DESIGN ---
PAGE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot Status | Server Monitor</title>
    <style>
        /* --- RESET & BASE STYLES --- */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #0d1117; /* GitHub Dark Dimmed */
            color: #c9d1d9;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }

        /* --- CONTAINER CARD --- */
        .container {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 2rem;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            position: relative;
        }

        /* --- HEADER & STATUS --- */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid #30363d;
            padding-bottom: 1rem;
        }
        
        .title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #58a6ff; /* Blue accent */
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-badge {
            background: rgba(35, 134, 54, 0.2);
            color: #3fb950; /* Green accent */
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            border: 1px solid rgba(35, 134, 54, 0.4);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .pulsing-dot {
            width: 8px;
            height: 8px;
            background-color: #3fb950;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        /* --- TERMINAL WINDOW LOOK --- */
        .terminal {
            background: #010409;
            border-radius: 6px;
            padding: 1.5rem;
            font-size: 0.9rem;
            border: 1px solid #30363d;
            min-height: 150px;
        }

        .line {
            margin-bottom: 8px;
            display: flex;
        }
        .prompt { color: #8b949e; margin-right: 10px; user-select: none; }
        .cmd { color: #c9d1d9; }
        .output { color: #79c0ff; }
        .cursor {
            display: inline-block;
            width: 8px;
            height: 15px;
            background: #c9d1d9;
            animation: blink 1s step-end infinite;
            vertical-align: middle;
        }

        /* --- ANIMATIONS --- */
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.4); }
            70% { box-shadow: 0 0 0 6px rgba(63, 185, 80, 0); }
            100% { box-shadow: 0 0 0 0 rgba(63, 185, 80, 0); }
        }
        @keyframes blink { 50% { opacity: 0; } }

        /* --- FOOTER --- */
        .footer {
            margin-top: 1.5rem;
            font-size: 0.75rem;
            color: #8b949e;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 17l6-6-6-6M12 19h8"></path>
                </svg>
                BOT_CONTROLLER
            </div>
            <div class="status-badge">
                <div class="pulsing-dot"></div>
                SYSTEM ONLINE
            </div>
        </div>

        <div class="terminal">
            <div class="line">
                <span class="prompt">$</span>
                <span class="cmd">check_status --service=telegram_bot</span>
            </div>
            <div class="line">
                <span class="prompt">></span>
                <span class="output">Connection established securely.</span>
            </div>
             <div class="line">
                <span class="prompt">></span>
                <span class="output">Listening for webhooks...</span>
            </div>
            <div class="line">
                <span class="prompt">></span>
                <span class="output">Database connection: OK (Google Sheets)</span>
            </div>
            <div class="line">
                <span class="prompt">$</span>
                <span class="cmd"><span class="cursor"></span></span>
            </div>
        </div>

        <div class="footer">
            RUNNING ON RENDER CLOUD • PYTHON 3.x • FLASK SERVER
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return PAGE_CONTENT

def run():
    # Render menggunakan environment variable PORT, jika tidak ada default ke 8080
    port = int(os.environ.get("PORT", 8080)) 
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # Pastikan thread mati saat program utama mati
    t.start()