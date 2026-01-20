from flask import Flask, render_template, request, jsonify
import threading
import time
import sys
import traceback  # Asli error dikhane ke liye

# Bot logic import karne ki koshish
print("Bot logic load ho raha hai...")
try:
    from bot_logic import FF_CLIENT
    print("Success: Bot logic mil gaya!")
except Exception as e:
    print("\n" + "="*40)
    print("[ERROR] 'bot_logic.py' load nahi ho paya!")
    print("Reason: Koi library missing hai ya code me error hai.")
    print("ASLI ERROR NEECHE DEKHO:")
    print("-" * 20)
    print(traceback.format_exc())  # Ye asli error print karega
    print("="*40 + "\n")
    sys.exit()

app = Flask(__name__)

# Background process function
def start_attack_process(uid, password, duration):
    try:
        print(f"[WEBSITE] Starting bot for UID: {uid}")
        # Bot instance create karo
        bot_instance = FF_CLIENT(uid, password)
        # Wait for duration
        time.sleep(int(duration))
        print(f"[WEBSITE] Time finished for UID: {uid}.")
    except Exception as e:
        print(f"[WEBSITE] Error in background process: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_bot():
    uid = request.form.get('uid')
    password = request.form.get('password')
    time_duration = request.form.get('time')

    if not uid or not password or not time_duration:
        return jsonify({"status": "error", "message": "Details missing!"})

    t = threading.Thread(target=start_attack_process, args=(uid, password, time_duration))
    t.daemon = True
    t.start()

    return jsonify({
        "status": "success", 
        "message": f"Bot Running: {uid} for {time_duration}s"
    })

if __name__ == '__main__':
    print("Website start ho rahi hai... http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
