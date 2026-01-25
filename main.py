from flask import Flask, render_template, request, jsonify
import threading
import time
import traceback
import requests
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# Agar tumhara bot baar-baar off ho raha hai, to yahan apna Render URL daal do
# Example: SITE_URL = "https://my-ffbot-v1.onrender.com"
SITE_URL = "https://ffbot-likho-3.onrender.com"  

# Data Storage
RUNNING_BOTS = {}

# --- BOT LOGIC IMPORT ---
try:
    from bot_logic import FF_CLIENT
    print("[SYSTEM] Bot Logic Loaded Successfully!")
except Exception as e:
    print(f"[ERROR] bot_logic.py load nahi hua! Error: {e}")
    def FF_CLIENT(u, p):
        print(f"[FAKE BOT] Logic missing for {u}")
        # Agar asli file nahi mili to ye error dega
        # raise Exception("Bot Logic File Missing") 

# --- KEEP ALIVE SYSTEM (Auto-Ping) ---
def keep_alive():
    if SITE_URL == "YOUR_RENDER_URL_HERE":
        print("[INFO] Auto-Ping disabled. Set SITE_URL in main.py to enable.")
        return

    while True:
        try:
            time.sleep(300) # Har 5 minute me ping karega
            response = requests.get(SITE_URL)
            print(f"[AUTO-WAKE] Pinged {SITE_URL} - Status: {response.status_code}")
        except Exception as e:
            print(f"[AUTO-WAKE] Ping Failed: {e}")

# Start Keep Alive Thread
threading.Thread(target=keep_alive, daemon=True).start()

# --- WORKER FUNCTION ---
def background_worker(uid, password, duration_seconds):
    global RUNNING_BOTS
    try:
        print(f"[BOT START] Connecting UID: {uid}...")
        
        # ASLI CONNECTION YAHAN HOGA
        FF_CLIENT(uid, password) 
        
        print(f"[BOT SUCCESS] {uid} is now Online!")
        
        # Timer Loop
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            if uid not in RUNNING_BOTS or RUNNING_BOTS[uid]['stop']: 
                print(f"[BOT STOP] Stopping {uid}...")
                break
            
            RUNNING_BOTS[uid]['elapsed'] = int(time.time() - start_time)
            time.sleep(1)
            
    except Exception as e:
        print(f"[BOT ERROR] {uid} Error: {e}")
        traceback.print_exc()
    finally:
        if uid in RUNNING_BOTS: del RUNNING_BOTS[uid]
        print(f"[BOT END] {uid} Process Finished.")

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_bot():
    name = request.form.get('name')
    uid = request.form.get('uid')
    password = request.form.get('password')
    raw_time = request.form.get('time')
    unit = request.form.get('unit')

    if not uid or not password: return jsonify({"status": "error", "message": "UID/Pass Missing!"})
    if uid in RUNNING_BOTS: return jsonify({"status": "error", "message": "Bot already running!"})

    try:
        duration = int(raw_time)
        if unit == "min": duration *= 60
        elif unit == "hours": duration *= 3600
        elif unit == "days": duration *= 86400
        elif unit == "permanent": duration = 999999999
    except:
        return jsonify({"status": "error", "message": "Invalid Time!"})

    RUNNING_BOTS[uid] = {
        'name': name if name else uid,
        'uid': uid,
        'password': password, 
        'stop': False,
        'elapsed': 0,
        'total_time': duration
    }

    t = threading.Thread(target=background_worker, args=(uid, password, duration))
    t.daemon = True
    t.start()
    
    return jsonify({"status": "success", "message": f"Command Sent to {uid}!"})

@app.route('/stop', methods=['POST'])
def stop_bot():
    uid = request.form.get('uid')
    if uid in RUNNING_BOTS:
        RUNNING_BOTS[uid]['stop'] = True
        return jsonify({"status": "success", "message": "Stop Command Sent"})
    return jsonify({"status": "error", "message": "Bot not found"})

@app.route('/active_bots')
def get_active_bots():
    return jsonify(RUNNING_BOTS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
