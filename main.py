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
    aqi, tvoc, eco2, _, _, eco2_rating = sensor_ens160.read_air_quality()
    
    # Read temperature and humidity from AHT21
    temp_aht21 = sensor_aht21.temperature
    rh_aht21 = sensor_aht21.relative_humidity
    temp_aht21_F = sensor_aht21.temperature * 1.8 + 32
    
    print(f"AQI: {aqi}")
    print(f"TVOC: {tvoc} ppb")
    print(f"eCO2: {eco2} ppm")
    print(f"Temperature (ENS160): {temp_aht21_F:.2f} °F")  # Adjust based on actual sensor data format
    print(f"Humidity (ENS160): {rh_aht21:.2f} %")   # Print humidity as a percentage
    print(f"eCO2 Rating: {eco2_rating}")
    
    time.sleep(2)  # Delay between readings