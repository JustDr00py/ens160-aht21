from machine import I2C

class ENS160:
    def __init__(self, i2c, address=0x53):
        self.i2c = i2c
        self.address = address
        self.set_mode(0x02)

    def _read_register(self, reg, length):
        return self.i2c.readfrom_mem(self.address, reg, length)

    def _write_register(self, reg, data):
        self.i2c.writeto_mem(self.address, reg, data)

    def set_mode(self, mode):
        self._write_register(0x10, bytes([mode]))  # Operating Mode

    def get_id(self):
        data = self._read_register(0x00, 2)  # Device Identity
        return (data[0] << 8) | data[1]

    def get_firmware_version(self):
        data = self._read_register(0x02, 2)  # Firmware Version
        return (data[0] << 8) | data[1]

    def get_status(self):
        data = self._read_register(0x20, 1)  # Operating Mode
        return data[0]
    
    def get_aqi(self):
        data = self._read_register(0x21, 1)  # Air Quality Index
        aqi_uba = data[0] & 0x07  # Extract the lower 3 bits
        return aqi_uba
    
    def get_tvoc(self):
        data = self._read_register(0x22, 2)  # TVOC Concentration (ppb)
        tvoc = (data[1] << 8) | data[0]  # LSB first, then MSB
        return tvoc

    def get_eco2(self):
        data = self._read_register(0x24, 2)  # Equivalent CO2 Concentration (ppm)
        eco2 = (data[1] << 8) | data[0]  # LSB first, then MSB
        return eco2

    def get_temperature(self):
        data = self._read_register(0x30, 2)  # Temperature used in calculations
        temp_raw = (data[0] << 8) | data[1]
        temp_kelvin = temp_raw / 64.0
        temp_celsius = temp_kelvin - 273.15
        return temp_celsius

    def get_humidity(self):
        data = self._read_register(0x32, 2)  # Relative Humidity used in calculations
        rh_raw = (data[0] << 8) | data[1]
        rh = rh_raw / 512.0  # Assuming the format is the same as ENS21x: RH% * 512
        return rh

    def interpret_eco2_level(self, eco2):
        if eco2 > 1500:
            return "Bad - Heavily contaminated indoor air / Ventilation required"
        elif eco2 > 1000:
            return "Poor - Contaminated indoor air / Ventilation recommended"
        elif eco2 > 800:
            return "Fair - Optional ventilation"
        elif eco2 > 600:
            return "Good - Average"
        elif eco2 >= 400:
            return "Excellent - Target level"
        else:
            return "Unknown"

    def interpret_tvoc_level(self, tvoc):
        if tvoc <= 50:
            return "Excellent"
        elif tvoc <= 100:
            return "Good"
        elif tvoc <= 150:
            return "Moderate"
        elif tvoc <= 200:
            return "Unhealthy"
        elif tvoc <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    def read_air_quality(self):
        aqi = self.get_aqi()
        tvoc = self.get_tvoc()
        eco2 = self.get_eco2()
        temp = self.get_temperature()
        rh = self.get_humidity()
        eco2_rating = self.interpret_eco2_level(eco2)
        tvoc_rating = self.interpret_tvoc_level(tvoc)
        return aqi, tvoc, eco2, temp, rh, eco2_rating, tvoc_rating

