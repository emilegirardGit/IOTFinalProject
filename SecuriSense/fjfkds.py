import RPi.GPIO as GPIO
import time
import requests
import json
from datetime import datetime
import geocoder

# Constants
upload_url = 'http://10.0.0.119:5000/uploadAlert'
log_file_path = '/alerts.json'

# GPIO pin setup
GPIO.setmode(GPIO.BCM)
laser_pin = 4
pin = 5
photoresistor_pin = 17
buzzer_pin = 27

GPIO.setup(laser_pin, GPIO.OUT)
GPIO.setup(pin, GPIO.OUT)
GPIO.setup(photoresistor_pin, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)

# Function to get current location
def get_current_location():
    g = geocoder.ip('me')
    return g.latlng

try:
    GPIO.output(laser_pin, GPIO.HIGH)
    GPIO.output(pin, GPIO.HIGH)

    # Loop to check the photoresistor and trigger actions
    while True:
        value = GPIO.input(photoresistor_pin)
        print(f"Photoresistor value: {value}")

        if value == 0:
            GPIO.output(buzzer_pin, GPIO.HIGH)
            current_location = get_current_location()
            data = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'location': f"{current_location[0]}, {current_location[1]}"
            }
            try:
                response = requests.post(upload_url, json=data)
                if response.status_code == 200:
                    print("JSON data uploaded successfully!")
                else:
                    print("Failed to upload JSON data. Status code:", response.status_code)
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
    GPIO.cleanup()  # Clean up the GPIO pins
