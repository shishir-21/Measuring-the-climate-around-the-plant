import adafruit_dht
import time
from datetime import datetime
import csv
import RPi.GPIO as GPIO
import board
import os
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Initialize DHT22 sensor
dht_sensor = adafruit_dht.DHT22(board.D4)

# Initialize ADC
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)  # Chip select pin
mcp = MCP.MCP3008(spi, cs)
channel = AnalogIn(mcp, MCP.P0)  # Assuming the moisture sensor is connected to CH0

# Initialize CSV file for logging sensor data
fieldname = ["Date", "Temp", "Humidity", "Moisture"]
with open("soil_data.csv", "a") as f1:
    writer = csv.DictWriter(f1, fieldnames=fieldname)
    writer.writeheader()

def read_sensor_data():
    # Read temperature and humidity from DHT22 sensor
    temperature = dht_sensor.temperature
    humidity = dht_sensor.humidity
    if humidity is not None and temperature is not None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Timestamp: {timestamp}")
        print(f"Temperature: {temperature:.2f}°C")
        print(f"Humidity: {humidity:.2f}%")
        return [timestamp, temperature, humidity]
    else:
        print("Failed to retrieve sensor data")

def read_soil_moisture_data():
    # Read moisture level from soil moisture sensor using ADC
    moisture_value = channel.value
    # Convert the ADC value to a percentage or any appropriate scale
    # You may need to calibrate this based on your sensor and environment
    moisture_percentage = (moisture_value / 65535) * 100  # Assuming 16-bit ADC
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Timestamp: {timestamp}")
    print(f"Soil Moisture: {moisture_percentage}%")
    return moisture_percentage

def write_data(sensor_data, moisture):
    # Write sensor data to CSV file
    with open("soil_data.csv", "a") as f1:
        writer = csv.DictWriter(f1, fieldnames=fieldname)
        writer.writerow({"Date": sensor_data[0], "Temp": sensor_data[1], "Humidity": sensor_data[2], "Moisture": str(moisture)})

try:
    num_photos = 100000  # Define the number of photos to capture
    base_string = "photo"  # Define the base string for file names

    # Loop for capturing photos and logging sensor data
    for i in range(num_photos):
        # Read sensor data
        sensor_data = read_sensor_data()
        moisture = read_soil_moisture_data()

        # Write sensor data to CSV file
        write_data(sensor_data, moisture)

        # Capture photo and save with unique filename
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{base_string}{current_time}{i}.jpg"
        os.system(f"libcamera-still -o /home/bcrec/Pictures/{file_name} -t 10 -n")

        # Add a delay between captures
        time.sleep(60)  # Adjust delay time as needed

except KeyboardInterrupt:
    print("Exiting...")

GPIO.cleanup()
