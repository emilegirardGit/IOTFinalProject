import base64
import hashlib
import json
import time
from datetime import datetime
import flask
import dbManager
import os
import threading
from dbManager import *
from flask import request, jsonify, render_template, redirect, g

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
    user = dbManager.getUsers(username, g.conn, g.cur)
    # Perform authentication here (e.g., check username and password against a database)

    if verify_password(password, user[6], user[2]):
        # Successful login, redirect to a different page or perform actions
        user_is_logged_in = True
        return redirect("/dashboard")
    else:
        # Invalid credentials, redirect back to the login page with a message
        return render_template('log_in_template.html', message='Invalid credentials. Please try again.')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register_template.html')

@app.route('/register', methods=['POST'])
def register_user():
    if not dbManager.getUsers(request.form['username'], g.conn, g.cur):
        salt, hashedPassword = hash_password(request.form['password'])
        user = (request.form['username'], hashedPassword, request.form['email'], request.form['address'], request.form['phone'], salt)
        dbManager.create_user(user, g.conn, g.cur)
        return redirect("/login")
    else:
        return render_template('register_template.html', message='Username is already taken')


@app.route('/logout', methods=['GET'])
def logout():
    global user_is_logged_in
    user_is_logged_in = False
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


# Part 1 Sales report
# Get request showing the sales with hard coded values


from datetime import datetime
from flask import render_template


# Your existing route definition remains the same

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


# Part 2 Temperature
# Get request that display the graph of the temperature
@app.route('/sample', methods=['GET'])
def sample():
    return render_template(
        "line_graph_example.html",
        data=temperature_data,
        labels=labels,
        header="Temperature Over Time",
        description="Graph shows temperature changes over time."
    )


# Post request getting the data from the raspberrypi
@app.route('/update-temperature', methods=['POST'])
def update_temperature():
    global index
    global labels
    global temperature_data
    data = request.json
    temperature_data = []
    index = 1
    labels = []
    # For each value in the json file is appended to the temperature_data array
    for value in data:
        temperature_data.append(value['temperature'])
        labels.append(index)
        index = index + 1

    # Return the function home to update the value on the website
    return sample()


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


@app.route('/offlineUpload', methods=['POST'])
def post_offline_upload_data():
    data = request.get_json()

    if not data:
        for value in data:
            date = value['date']
            location = value['location']
            image = value['image']

            alert = (location, image, date)
            dbManager.create_alert(alert, g.conn, g.cur)
        # Send a response
        return jsonify({'message': 'offline data has been received and processed!'}), 200
    print("Offline data was empty")


@app.route('/uploadImageTest', methods=['POST'])
def upload_Image_Test():
    data = request.get_json()
    image = data.get('image')

    with open('received.png', 'wb') as img_file:
        img_file.write(image.decode('base64'))

    # Send a response
    return jsonify({'message': 'Image received!'}), 200


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

def hash_password(password):
    # Generate a random salt
    salt = os.urandom(16)

    # Combine the password and the salt, and hash them
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    print(hashed_password)
    print(salt)
    # Return the salt and the hashed password
    return salt, hashed_password


def verify_password(input_password, stored_salt, stored_hash):
    # Hash the input password with the stored salt
    new_hash = hashlib.pbkdf2_hmac('sha256', input_password.encode('utf-8'), stored_salt, 100000)
    print(new_hash)
    print(stored_hash)
    print(stored_salt)
    return new_hash == stored_hash



# Start the thread for file deletion
delete_thread = threading.Thread(target=delete_alerts_file)
delete_thread.daemon = True  # Set as daemon to terminate when main program exits
delete_thread.start()

# Run the flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
