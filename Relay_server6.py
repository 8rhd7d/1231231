from flask import Flask, request
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app)

# Disable Flask logging spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ============================================================
# State
# ============================================================
latest_id = None

# ============================================================
# Routes
# ============================================================

@app.route('/latest')
def get_latest():
    """Get the latest game instance ID."""
    global latest_id
    return latest_id if latest_id else "", 200, {'Content-Type': 'text/plain'}

@app.route('/post/<game_id>')
def post_id_get(game_id):
    """Post a new game instance ID via GET (legacy support for UUID)."""
    global latest_id
    
    # Accept UUIDs (36 chars) or long hex strings (64+ chars)
    if len(game_id) == 36 or len(game_id) >= 64:
        latest_id = game_id
        print(f"✅ New ID (GET): {game_id[:20]}{'...' if len(game_id) > 20 else ''}")
        return "OK"
    
    return "Invalid ID", 400

@app.route('/post', methods=['POST'])
def post_id_json():
    """Post a new game instance ID via POST with JSON body."""
    global latest_id
    
    try:
        data = request.get_json()
        game_id = data.get('id', '')
        
        # Accept UUIDs (36 chars) or long hex strings (64+ chars)
        if len(game_id) == 36 or len(game_id) >= 64:
            latest_id = game_id
            print(f"✅ New ID (POST): {game_id[:20]}{'...' if len(game_id) > 20 else ''}")
            return "OK", 200
        
        return "Invalid ID", 400
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Bad Request", 400

@app.route('/clear')
def clear():
    """Clear the current ID."""
    global latest_id
    latest_id = None
    print("🗑️ ID cleared")
    return "OK"

@app.route('/')
def home():
    """Status page."""
    global latest_id
    
    # Format ID display for long hex strings
    if latest_id and len(latest_id) > 40:
        display_id = f"{latest_id[:20]}...{latest_id[-20:]}<br><small style='color: #8b949e;'>(Full length: {len(latest_id)} chars)</small>"
    else:
        display_id = latest_id if latest_id else 'Waiting for game instance...'
    
    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="2">
        <style>
            body {{
                background: #0d1117;
                color: #58a6ff;
                font-family: monospace;
                padding: 40px;
                text-align: center;
            }}
            h1 {{ color: #58a6ff; }}
            #id {{
                font-size: 18px;
                padding: 20px;
                background: #161b22;
                border-radius: 8px;
                margin: 20px auto;
                max-width: 800px;
                word-break: break-all;
                line-height: 1.6;
            }}
            .stats {{
                color: #8b949e;
                font-size: 12px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <h1>🎮 Game Instance Relay</h1>
        <div id="id">{display_id}</div>
        <p style="color: #8b949e; font-size: 14px;">Auto-refreshes every 2 seconds</p>
        <div class="stats">
            Supports: UUID (36 chars) & Hex IDs (64+ chars)
        </div>
    </body>
    </html>
    """

# ============================================================
# Run
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("🚀 Relay Server Running on port", port)
    print("📡 Accepting UUIDs (36 chars) and Long Hex IDs (64+ chars)")
    app.run(host='0.0.0.0', port=port, debug=False)