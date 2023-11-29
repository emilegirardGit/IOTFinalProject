import subprocess
from flask import Flask

app = Flask(__name__)

security_process = None  # Global variable to store the security.py process

@app.route('/start_command', methods=['POST'])
def start_command():
    global security_process

    if security_process and security_process.poll() is None:
        return 'Security program is already running'

    security_process = subprocess.Popen(['python3', 'security.py'])
    return 'Python program started'

@app.route('/stop_command', methods=['POST'])
def stop_command():
    global security_process

    if security_process and security_process.poll() is None:
        security_process.terminate()
        security_process = None
        return 'Python program stopped'

    return 'Python program is not running'

# @app.route('/status', methods=['GET'])
# def status():
#     global security_process
#
#     if security_process and security_process.poll() is None:
#         return jsonify({'status': 'running'}), 200
#     else:
#         return jsonify({'status': 'stopped'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


