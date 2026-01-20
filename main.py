from flask import Flask, render_template, request, jsonify
import threading
import time

app = Flask(__name__)

# Data Storage
RUNNING_BOTS = {}

# Bot Logic Placeholder
try:
    from bot_logic import FF_CLIENT
except Exception:
    pass 

def background_worker(uid, password, duration_seconds):
    global RUNNING_BOTS
    try:
        # FF_CLIENT(uid, password) # Asli bot logic yahan call hoga
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            if uid not in RUNNING_BOTS or RUNNING_BOTS[uid]['stop']: break
            RUNNING_BOTS[uid]['elapsed'] = int(time.time() - start_time)
            time.sleep(1)
    except Exception as e:
        print(f"Error {uid}: {e}")
    finally:
        if uid in RUNNING_BOTS: del RUNNING_BOTS[uid]

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

    if not uid or not password: return jsonify({"status": "error", "message": "Details missing!"})
    if uid in RUNNING_BOTS: return jsonify({"status": "error", "message": "Already Running!"})

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
    return jsonify({"status": "success", "message": "Bot Started!"})

@app.route('/stop', methods=['POST'])
def stop_bot():
    uid = request.form.get('uid')
    if uid in RUNNING_BOTS:
        RUNNING_BOTS[uid]['stop'] = True
        return jsonify({"status": "success", "message": "Stopped"})
    return jsonify({"status": "error", "message": "Not Found"})

@app.route('/active_bots')
def get_active_bots():
    return jsonify(RUNNING_BOTS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
