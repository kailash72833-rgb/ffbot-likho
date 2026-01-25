from flask import Flask, render_template, request, jsonify
import threading
import time
import traceback
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
# Yahan apna Render URL daal dena agar Auto-Wake chahiye
SITE_URL = "https://ffbot-likho-3.onrender.com"  

# Data Storage
# Structure: {'UID123': {'status': 'RUNNING', 'start_time': 12345, ...}}
ALL_BOTS = {}

# --- BOT LOGIC IMPORT ---
try:
    from bot_logic import FF_CLIENT
    print("[SYSTEM] Bot Logic Loaded Successfully!")
except Exception as e:
    print(f"[ERROR] Logic load failed: {e}")
    def FF_CLIENT(u, p): pass

# --- AUTO WAKE SYSTEM ---
def keep_alive():
    while True:
        try:
            time.sleep(300) 
            if "YOUR_RENDER_URL" not in SITE_URL:
                requests.get(SITE_URL)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

# --- WORKER FUNCTION ---
def background_worker(uid, duration_seconds):
    global ALL_BOTS
    
    try:
        print(f"[BOT START] {uid}")
        # Mark as RUNNING
        ALL_BOTS[uid]['status'] = 'RUNNING'
        ALL_BOTS[uid]['active'] = True
        
        # ASLI ATTACK START
        FF_CLIENT(uid, ALL_BOTS[uid]['password']) 
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            # Agar user ne stop button dabaya
            if ALL_BOTS[uid].get('stop_req'):
                print(f"[BOT STOPPED] {uid} by User")
                break
            
            # Update Time
            ALL_BOTS[uid]['elapsed'] = int(time.time() - start_time)
            time.sleep(1)
            
    except Exception as e:
        print(f"[ERROR] {uid}: {e}")
    finally:
        # IMPORTANT: Delete nahi karenge, bas status 'OFF' karenge
        if uid in ALL_BOTS:
            ALL_BOTS[uid]['status'] = 'OFF'
            ALL_BOTS[uid]['active'] = False
            print(f"[BOT END] {uid} moved to OFF section")

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

    # Agar bot pehle se list me hai aur RUNNING hai to error do
    if uid in ALL_BOTS and ALL_BOTS[uid]['active']:
        return jsonify({"status": "error", "message": "Ye Bot pehle se RUNNING hai!"})

    # Time Calculation
    try:
        duration = int(raw_time)
        if unit == "min": duration *= 60
        elif unit == "hours": duration *= 3600
        elif unit == "days": duration *= 86400
        elif unit == "permanent": duration = 999999999
    except:
        return jsonify({"status": "error", "message": "Invalid Time!"})

    # Bot ko list me add/update karo
    ALL_BOTS[uid] = {
        'name': name if name else uid,
        'uid': uid,
        'password': password,
        'status': 'STARTING...',
        'active': True,
        'stop_req': False,
        'elapsed': 0,
        'total_time': duration
    }

    t = threading.Thread(target=background_worker, args=(uid, duration))
    t.daemon = True
    t.start()
    
    return jsonify({"status": "success", "message": f"Bot {uid} Started!"})

@app.route('/stop', methods=['POST'])
def stop_bot():
    uid = request.form.get('uid')
    if uid in ALL_BOTS and ALL_BOTS[uid]['active']:
        ALL_BOTS[uid]['stop_req'] = True
        return jsonify({"status": "success", "message": "Stopping..."})
    return jsonify({"status": "error", "message": "Bot already OFF or not found"})

@app.route('/active_bots')
def get_active_bots():
    return jsonify(ALL_BOTS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
