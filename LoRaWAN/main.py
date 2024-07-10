from machine import I2C, Pin, UART
from ens160 import ENS160
from ahtx0 import AHT20  # Assuming AHT20 is compatible with AHT21 and supported by ahtx0 library
import time
import ubinascii

# Initialize I2C interface (adjust pins and frequency as needed)
i2c = I2C(1, scl=Pin(25), sda=Pin(26), freq=100000)

# Initialize the ENS160 sensor
sensor_ens160 = ENS160(i2c)

# Initialize the AHT21 sensor
sensor_aht21 = AHT20(i2c)

# Initialize UART for RAK3272S communication
uart1 = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))

# Offset for temperature adjustment (in Celsius)
temperature_offset = -10.0  # Adjust this value as needed

def send_at_command(command, timeout=1000):
    uart1.write(command.encode() + b'\r\n')
    time.sleep_ms(timeout)
    response = uart1.read()
    return response.decode() if response else 'No Response'

def join_ttn():
    # Join the network
    response = send_at_command('AT+JOIN=1:0:10:8')
    print(response)
    if "OK" in response:
        print("Successfully joined the network!")
    else:
        print("Failed to join the network.")

def send_payload(payload):
    hex_payload = ubinascii.hexlify(payload)
    print("Sending payload:", hex_payload.decode())  # Print hex representation of payload
    response = send_at_command(f'AT+SEND=1:{hex_payload.decode()}')
    print(response)

# Join TTN before sending data
join_ttn()

# Main loop to read and send sensor data
while True:
    aqi, tvoc, eco2, eco2_rating, tvoc_rating = sensor_ens160.read_air_quality()
    
    # Read temperature and humidity from AHT21
    temp_aht21 = sensor_aht21.temperature  # Apply offset
    
    rh_aht21 = sensor_aht21.relative_humidity
    temp_aht21_F = temp_aht21 * 1.8 + 32 + temperature_offset  # Convert to Fahrenheit
    
    # Create payload
    payload = bytearray()
    payload.append(aqi)
    payload.extend(tvoc.to_bytes(2, 'big'))
    payload.extend(eco2.to_bytes(2, 'big'))
    payload.extend(int(temp_aht21_F * 100).to_bytes(2, 'big'))
    payload.extend(int(rh_aht21 * 100).to_bytes(2, 'big'))
    
    # Print sensor data
    print(f"AQI: {aqi}")
    print(f"TVOC: {tvoc} ppb")
    print(f"TVOC Rating: {tvoc_rating}")
    print(f"eCO2: {eco2} ppm")
    print(f"Temperature (ENS160): {temp_aht21_F:.2f} °F")
    print(f"Humidity (ENS160): {rh_aht21:.2f} %")
    print(f"eCO2 Rating: {eco2_rating}")
    
    # Send payload to TTN
    send_payload(payload)
    
    time.sleep(60)  # Delay between readings
