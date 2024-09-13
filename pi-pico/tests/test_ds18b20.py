import machine
import onewire
import ds18x20
import time

# Define the GPIO pin where the DS18B20 data line is connected
DS18B20_PIN = 2  # Change this to the GPIO pin you're using

# Initialize the 1-Wire bus
ow = onewire.OneWire(machine.Pin(DS18B20_PIN))

# Create the DS18X20 object
ds_sensor = ds18x20.DS18X20(ow)

def scan_for_devices():
    """Scan for DS18B20 devices on the 1-Wire bus."""
    devices = ds_sensor.scan()
    print(f"Found {len(devices)} DS18B20 device(s)")
    return devices

def read_temperature(devices):
    """Read temperature from all found devices."""
    ds_sensor.convert_temp()
    # The sensor needs at least 750ms to convert the temperature
    time.sleep_ms(200)
    
    for device in devices:
        try:
            temp = ds_sensor.read_temp(device)
            print(f"Sensor {device.hex()} temperature: {temp:.2f}°C")
        except Exception as e:
            print(f"Error reading sensor {device.hex()}: {e}")

def main():
    print("DS18B20 Temperature Sensor Test")
    print("===============================")
    
    devices = scan_for_devices()
    
    if not devices:
        print("No DS18B20 devices found. Check your wiring.")
        return
    
    print("\nStarting temperature readings:")
    for _ in range(10):  # Read temperature 10 times
        read_temperature(devices)

if __name__ == "__main__":
    main()