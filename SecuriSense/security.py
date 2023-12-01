import RPi.GPIO as GPIO
import time
import cv2
import base64
import requests
import json
from datetime import datetime
import socket



# Constants
upload_url = 'http://10.0.0.119:5000/uploadAlert'
connection_check_url = 'http://10.0.0.119:5000/connectionCheck'
log_file_path = '/tmp/alerts.json'

GPIO.setmode(GPIO.BCM)
laser_pin = 4
pin = 5
photoresistor_pin = 17
buzzer_pin = 27
isOnline = True
wasOnlineBefore = False
GPIO.setup(laser_pin, GPIO.OUT)
GPIO.setup(pin, GPIO.OUT)
GPIO.setup(photoresistor_pin, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)
cap = cv2.VideoCapture(0)
cameraIsWorking = True
if not cap.isOpened():
    cameraIsWorking = False

# Function to get current location
def get_current_location():
    if isOnline:
        try:
            import geocoder
            g = geocoder.ip('me')
            return g.latlng
        except ModuleNotFoundError:
            print("Geocoder module not found.")
            return 0, 0
    else:
        return 0, 0
def is_api_reachable():
    try:
        socket.create_connection(("10.0.0.119", 5000), timeout=2)  # Adjust timeout as needed
        return True
    except OSError:
        pass
    return False

def upload_offline_data():
    try:
        with open(log_file_path, 'r') as fh:
            lines = fh.readlines()
            for line in lines:
                data = json.loads(line)
                response = requests.post(upload_url, json=data)
                if response.status_code == 200:
                    print("Offline JSON data uploaded successfully!")
                    # Note: This removes only the successfully uploaded lines, so we don't lose any data.
                    lines.remove(line)
        # Write back the remaining lines to the log file (the ones that failed to upload)
        with open(log_file_path, 'w') as fh:
            fh.writelines(lines)
    except FileNotFoundError:
        print("No offline data found.")

try:
    GPIO.output(laser_pin, GPIO.HIGH)
    GPIO.output(pin, GPIO.HIGH)

    # Loop to check the photoresistor and trigger actions
    while True:

        api_reachable = is_api_reachable()
        if api_reachable:
            isOnline = True
            print("We are online!")
            if not wasOnlineBefore:
                upload_offline_data()
                wasOnlineBefore = True
        else:
            print("API is offline or unreachable")
            isOnline = False
            wasOnlineBefore = False

        value = GPIO.input(photoresistor_pin)
        print(f"Photoresistor value: {value}")

        if value == 0:




            #turn buzzer on
            GPIO.output(buzzer_pin, GPIO.HIGH)
            # Capture a frame from the webcam
            if cameraIsWorking:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture an image.")
                    img_base64 = None
                else:
                    print("Picture of location taken")
                    _, img_encoded = cv2.imencode('.jpg', frame)
                    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
            else:
                img_base64 = None
                print("Error: Camera is not working")
            current_location = get_current_location()
            data = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'location': f"{current_location[0]}, {current_location[1]}",
                'image': img_base64
            }
            try:
                if isOnline:
                    response = requests.post(upload_url, json=data)
                    if response.status_code == 200:
                        print("JSON data uploaded successfully!")
                    else:
                        print("Failed to upload JSON data. Status code:", response.status_code)
                        with open(log_file_path, 'a') as fh:
                            json.dump(data, fh)  # Inserting JSON OBJECT into File
                            fh.write('\n')
                else:
                    print("Offline Mode. Writing to file")
                    with open(log_file_path, 'a') as fh:
                        json.dump(data, fh)  # Inserting JSON OBJECT into File
                        fh.write('\n')
            except requests.RequestException as e:
                print("Error:", e)

            time.sleep(0.5)
            GPIO.output(buzzer_pin, GPIO.LOW)
        else:
            GPIO.output(buzzer_pin, GPIO.LOW)
        time.sleep(1)

except KeyboardInterrupt:  # Ctrl+C to exit the program
    pass

finally:
    GPIO.cleanup()
    cap.release()
    pass
