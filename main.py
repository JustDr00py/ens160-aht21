from machine import I2C, Pin
from ens160 import ENS160
from ahtx0 import AHT20  # Assuming AHT20 is compatible with AHT21 and supported by ahtx0 library
import time

# Initialize I2C interface (adjust pins and frequency as needed)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=100000)

# Initialize the ENS160 sensor
sensor_ens160 = ENS160(i2c)

# Initialize the AHT21 sensor
sensor_aht21 = AHT20(i2c)

# Main loop to read and print sensor data
while True:
    aqi, tvoc, eco2, temp, rh, eco2_rating, tvoc_rating = sensor_ens160.read_air_quality()
    
    print(f"AQI: {aqi}")
    print(f"TVOC: {tvoc} ppb")
    print(f"TVOC Rating: {tvoc_rating}")
    print(f"eCO2: {eco2} ppm")
    print(f"Temperature: {temp:.2f} °C")
    print(f"Humidity: {rh:.2f} %")
    print(f"eCO2 Rating: {eco2_rating}")
    
    time.sleep(2)  # Delay between readings
