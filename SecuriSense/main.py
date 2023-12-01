import json
import time
import flask
import dbManager
import os
import threading
import requests
from dbManager import *
from flask import request, jsonify, render_template, redirect, g
from datetime import datetime
from flask import render_template

app = flask.Flask(__name__)
app.config["DEBUG"] = True
alerts_file_path = 'alerts_data.json'
user_is_logged_in = False
index = 1  # index to keep track of the values


# default

@app.route('/', methods=['GET'])
def default():
    return redirect("/login")


# Route for displaying the login page
@app.route('/login', methods=['GET'])
def login():
    return render_template('log_in_template.html')


# Handle login form submission
@app.route('/login', methods=['POST'])
def login_user():
    global user_is_logged_in
    username = request.form['username']
    password = request.form['password']

    # Perform authentication here (e.g., check username and password against a database)

    # For simplicity, let's assume a hardcoded username and password for demonstration purposes
    if username == 'user' and password == 'pwd':
        # Successful login, redirect to a different page or perform actions
        user_is_logged_in = True
        return redirect("/dashboard")
    else:
        # Invalid credentials, redirect back to the login page with a message
        return render_template('log_in_template.html', message='Invalid credentials. Please try again.')


@app.route('/logout', methods=['GET'])
def logout():
    global user_is_logged_in
    user_is_logged_in = False
    return redirect('/login')


@app.route('/admin', methods=['GET'])
def admin():
    global user_is_logged_in
    # Check if the user is logged in
    if user_is_logged_in:
        alerts = dbManager.getAlertsInReverse(g.conn, g.cur)
        return render_template('admin.html', alerts=alerts)
    else:
        return redirect('/login')
@app.route('/dashboard', methods=['GET'])
def dashboard():
    global user_is_logged_in
    # Check if the user is logged in (You might use session management or authentication)
    # For simplicity, let's assume the user is logged in by checking a boolean variable
    # Replace this with your actual authentication logic
    if user_is_logged_in:
        return render_template('dashboard.html')
    else:
        # Redirect to login if the user is not logged in
        return redirect('/login')


@app.route('/graph', methods=['GET'])
def graph():
    # Define Plot Data
    label = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    data = [0] * len(label)  # Initialize data list with zeros for each month

    alerts = dbManager.getAlerts(g.conn, g.cur)

    for alert in alerts:
        alert_time_str = alert[3]  # Assuming the datetime is in the fourth index as a string
        alert_time = datetime.strptime(alert_time_str, '%Y-%m-%d %H:%M:%S')
        month = alert_time.month - 1  # Adjust month to match zero-based index

        # Increment the count for the corresponding month
        data[month] += 1

    print(data)

    return render_template(
        "line_graph_example.html",
        data=data,
        labels=label,
        header="Temperature Over Time",
        description="Graph shows temperature changes over time."
    )


@app.route('/uploadAlert', methods=['POST'])
def upload_data():
    data = request.get_json()

    # Access different fields from the JSON data
    date = data.get('date')
    location = data.get('location')
    image = data.get('image')

    alert = (location, image, date)
    dbManager.create_alert(alert, g.conn, g.cur)

    # Write data to the file
    write_to_file(data)

    # Send a response
    return jsonify({'message': 'JSON data received and processed!'}), 200


@app.route('/connectionCheck', methods=['GET'])
def connectionCheck():
    return 'Connection OK', 200
@app.route('/deleteAlerts', methods=['GET'])
def deleteAlerts():
    if user_is_logged_in:
        dbManager.deleteAllAlerts(g.conn,g.cur)
        return redirect("/admin")
    else:
        return redirect("/login")

# @app.route('/status', methods=['GET'])
# def status():
#     try:
#         response = requests.get('http://10.0.0.134:5001/status')  # Replace with your Raspberry Pi's IP and port
#         if response.status_code == 200:
#             data = response.json()
#             status = data.get('status')
#
#             if status == 'running':
#                 return jsonify({'status': 'running'}), 200
#             else:
#                 return jsonify({'status': 'stopped'}), 200
#         else:
#             return jsonify({'status': 'unreachable'}), 200
#
#     except requests.RequestException as e:
#         print("Error:", e)
#         return jsonify({'status': 'unreachable'}), 200

@app.route('/start_program', methods=['POST'])
def start_program():
    # Send a start command to Raspberry Pi
    response = requests.post('http://10.0.0.134:5001/start_command')
    if response.status_code == 200:
        return 'Python program started on Raspberry Pi'
    else:
        return 'Failed to start Python program on Raspberry Pi'

@app.route('/stop_program', methods=['POST'])
def stop_program():
    # Send a stop command to Raspberry Pi
    response = requests.post('http://10.0.0.134:5001/stop_command')
    if response.status_code == 200:
        return 'Python program stopped on Raspberry Pi'
    else:
        return 'Failed to stop Python program on Raspberry Pi'


@app.before_request
def before_request():
    g.conn = sqlite3.connect("securiSense.db")
    g.cur = g.conn.cursor()


@app.teardown_request
def teardown_request(exception=None):
    conn = getattr(g, 'conn', None)
    if conn:
        conn.close()


# Function to write data to file
def write_to_file(data):
    with open(alerts_file_path, 'a') as file:
        json.dump(data, file)
        file.write('\n')


# Function to delete the alerts file after a specified time
def delete_alerts_file():
    while True:
        if os.path.exists(alerts_file_path):
            os.remove(alerts_file_path)
        time.sleep(86400)  # Sleep for a day before deletion


# Start the thread for file deletion
delete_thread = threading.Thread(target=delete_alerts_file)
delete_thread.daemon = True  # Set as daemon to terminate when main program exits
delete_thread.start()

# Run the flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
