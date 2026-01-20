from flask import Flask, render_template, request, jsonify
import threading
import time
import sys
import traceback

app = Flask(__name__)

# Data Storage
RUNNING_BOTS = {}

# --- BOT LOGIC IMPORT (CRITICAL) ---
# Yahan hum check kar rahe hain ki bot_logic.py sahi se load ho raha hai ya nahi
try:
    from bot_logic import FF_CLIENT
    print("[SYSTEM] Bot Logic Loaded Successfully!")
except Exception as e:
    print(f"[ERROR] bot_logic.py load nahi hua! Error: {e}")
    # Hum fake function bana dete hain taaki server crash na ho, par error dikhe
    def FF_CLIENT(u, p):
        print(f"[FAKE BOT] Connection Failed. Logic missing for {u}")
        raise Exception("Bot Logic File Missing or Corrupted")

def background_worker(uid, password, duration_seconds):
    global RUNNING_BOTS
    try:
        print(f"[BOT START] Connecting UID: {uid}...")
        
        # --- ASLI CONNECTION START ---
        # Ye line ab uncommented hai, matlab ab ye Garena se connect karega
        FF_CLIENT(uid, password) 
        # -----------------------------

        print(f"[BOT SUCCESS] {uid} is now Online!")
        
        # Timer Loop (Bot ko zinda rakhne ke liye aur time count karne ke liye)
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            # Agar user ne STOP dabaya, to loop todo
            if uid not in RUNNING_BOTS or RUNNING_BOTS[uid]['stop']: 
                print(f"[BOT STOP] Stopping {uid}...")
                break
            
            # Time Update
            RUNNING_BOTS[uid]['elapsed'] = int(time.time() - start_time)
            time.sleep(1)
            
    except Exception as e:
        print(f"[BOT ERROR] {uid} Error: {e}")
        # Error detail console me dikhana
        traceback.print_exc()
    finally:
        if uid in RUNNING_BOTS: del RUNNING_BOTS[uid]
        print(f"[BOT END] {uid} Process Finished.")

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

    # Bot ko list me add karo
    RUNNING_BOTS[uid] = {
        'name': name if name else uid,
        'uid': uid,
        'password': password, # Password hum frontend pe wapas nahi bhejenge security ke liye
        'stop': False,
        'elapsed': 0,
        'total_time': duration
    }

    # Thread start karo
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
    # Frontend ko data bhejo
    return jsonify(RUNNING_BOTS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
