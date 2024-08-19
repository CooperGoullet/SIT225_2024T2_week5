import serial
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import json

# Initialize Firebase
cred = credentials.Certificate(r"C:\Users\Coope\Week 5\gyro-f67ef-firebase-adminsdk-yqcrf-ec5e096587.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gyro-f67ef-default-rtdb.firebaseio.com/'
})

ser = serial.Serial('COM9', 9600, timeout=1)  # Adjust 'COM3' to your port
ser.flush()

# Reference to the Firebase path
ref = db.reference("/sensor_data/L6DS3")

# Function to read and parse data from Serial
def parse_serial_data(line):
    parts = line.split(',')
    if len(parts) == 3:
        try:
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "x": x,
                "y": y,
                "z": z
            }
        except ValueError:
            return None
    return None

# Data collection loop
print("Collecting data.")
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            data = parse_serial_data(line)
            if data:
                ref.push(data)  # Upload data to Firebase
except KeyboardInterrupt:
    print("Data collection stopped.")

# Query data from Firebase
sensor_data = ref.get()

# Save data to CSV
if sensor_data:
    data_list = []
    for record in sensor_data.values():
        data_list.append(record)
    df = pd.DataFrame(data_list)
    df.to_csv('gyroscope_data.csv', index=False)
    print("Data saved to gyroscope_data.csv")
else:
    print("No data found in Firebase.")

