from flask import Flask, render_template, request, jsonify
import threading
import time
import traceback

app = Flask(__name__)

# Dictionary to store all running bots
# Structure: {'UID123': {'pass': 'abc', 'name': 'Bot1', 'status': 'Running', 'stop': False}}
RUNNING_BOTS = {}

# Bot Logic Import
try:
    from bot_logic import FF_CLIENT
except Exception:
    pass 

def background_worker(uid, password, duration_seconds):
    global RUNNING_BOTS
    
    try:
        print(f"[BOT] Starting {uid}")
        # Bot Login (Simulated logic here, replace with real FF_CLIENT)
        # FF_CLIENT(uid, password) 
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            # Check if user stopped this specific bot
            if uid not in RUNNING_BOTS or RUNNING_BOTS[uid]['stop']:
                print(f"[BOT] Stopped {uid} by User")
                break
            
            # Update elapsed time for frontend
            RUNNING_BOTS[uid]['elapsed'] = int(time.time() - start_time)
            time.sleep(1) 
            
    except Exception as e:
        print(f"[BOT] Error {uid}: {e}")
    finally:
        # Remove from list when finished
        if uid in RUNNING_BOTS:
            del RUNNING_BOTS[uid]
        print(f"[BOT] Finished {uid}")

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

    if not uid or not password or not raw_time:
        return jsonify({"status": "error", "message": "Details missing!"})

    if uid in RUNNING_BOTS:
        return jsonify({"status": "error", "message": "Ye UID pehle se chal raha hai!"})

    # Time Calculation
    try:
        duration = int(raw_time)
        if unit == "min": duration *= 60
        elif unit == "hours": duration *= 3600
        elif unit == "days": duration *= 86400
        elif unit == "permanent": duration = 31536000 # 1 Year (Practically permanent)
    except:
        return jsonify({"status": "error", "message": "Time invalid hai!"})

    # Add to dictionary
    RUNNING_BOTS[uid] = {
        'name': name if name else f"Bot-{uid[-4:]}",
        'uid': uid,
        'password': password,
        'stop': False,
        'elapsed': 0,
        'total_time': duration if duration < 30000000 else "PERMANENT"
    }

    t = threading.Thread(target=background_worker, args=(uid, password, duration))
    t.daemon = True
    t.start()

    return jsonify({"status": "success", "message": f"Bot {name} Started!"})

@app.route('/stop', methods=['POST'])
def stop_bot():
    uid = request.form.get('uid')
    if uid in RUNNING_BOTS:
        RUNNING_BOTS[uid]['stop'] = True
        return jsonify({"status": "success", "message": "Stopping..."})
    return jsonify({"status": "error", "message": "Bot not found"})

@app.route('/active_bots')
def get_active_bots():
    # Return list of all bots to frontend
    return jsonify(RUNNING_BOTS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
