from flask import Flask, render_template, request, jsonify
import threading
import time
import traceback

app = Flask(__name__)

# Global Control Flags
BOT_RUNNING = False
STOP_FLAG = False

# Bot Logic Import
try:
    from bot_logic import FF_CLIENT
except Exception:
    pass # Error handle frontend pe karenge

def background_worker(uid, password, duration_seconds):
    global BOT_RUNNING, STOP_FLAG
    BOT_RUNNING = True
    STOP_FLAG = False
    
    print(f"[BOT] Started for {duration_seconds} seconds")
    
    try:
        # Bot Login (Ek baar)
        FF_CLIENT(uid, password)
        
        # Loop for duration (taaki beech me rok sakein)
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            if STOP_FLAG:
                print("[BOT] Stopped by User")
                break
            time.sleep(1) # Har 1 second check karega
            
    except Exception as e:
        print(f"[BOT] Error: {e}")
    finally:
        BOT_RUNNING = False
        print("[BOT] Finished")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_bot():
    global BOT_RUNNING
    if BOT_RUNNING:
        return jsonify({"status": "error", "message": "Bot pehle se chal raha hai!"})

    uid = request.form.get('uid')
    password = request.form.get('password')
    raw_time = request.form.get('time')
    unit = request.form.get('unit')

    if not uid or not password or not raw_time:
        return jsonify({"status": "error", "message": "Details missing!"})

    # Time Calculation
    try:
        duration = int(raw_time)
        if unit == "min": duration *= 60
        elif unit == "hours": duration *= 3600
        elif unit == "days": duration *= 86400
        elif unit == "permanent": duration = 99999999 # Unlimited
    except:
        return jsonify({"status": "error", "message": "Time invalid hai!"})

    t = threading.Thread(target=background_worker, args=(uid, password, duration))
    t.daemon = True
    t.start()

    return jsonify({"status": "success", "message": "Bot Started!", "total_seconds": duration})

@app.route('/stop', methods=['POST'])
def stop_bot():
    global STOP_FLAG, BOT_RUNNING
    if not BOT_RUNNING:
        return jsonify({"status": "error", "message": "Bot chal hi nahi raha."})
    
    STOP_FLAG = True
    return jsonify({"status": "success", "message": "Bot Stopping..."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
