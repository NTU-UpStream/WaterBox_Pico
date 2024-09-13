from machine import I2C, Pin
from ads1x15 import ADS1115
import utime

# Power up ADS1115
power = Pin(6, Pin.OUT)
power.on()
utime.sleep(1)

# Initialize I2C0
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=40000)

# Initialize ADS1115
ads = ADS1115(i2c, address=0x48, gain=1)

def test_single_ended():
    print("Testing single-ended measurements:")
    for channel in range(4):
        value = ads.read(channel1=channel)
        voltage = ads.raw_to_v(value)
        print(f"Channel {channel}: Raw={value}, Voltage={voltage:.6f}V")
    print()

def test_differential():
    print("Testing differential measurements:")
    diff_channels = [(0, 1), (0, 3), (1, 3), (2, 3)]
    for ch1, ch2 in diff_channels:
        value = ads.read(channel1=ch1, channel2=ch2)
        voltage = ads.raw_to_v(value)
        print(f"Differential {ch1}-{ch2}: Raw={value}, Voltage={voltage:.6f}V")
    print()

def test_continuous_conversion():
    print("Testing continuous conversion mode:")
    ads.conversion_start(channel1=0)
    for _ in range(10):
        value = ads.alert_read()
        voltage = ads.raw_to_v(value)
        print(f"Continuous read: Raw={value}, Voltage={voltage:.6f}V")
        utime.sleep_ms(100)
    print()

def test_alert_mode():
    print("Testing alert mode:")
    threshold_high = 10000  # Adjust this value based on your input voltage
    threshold_low = -10000  # Adjust this value based on your input voltage
    ads.alert_start(channel1=0, threshold_high=threshold_high, threshold_low=threshold_low, latched=True)
    for _ in range(10):
        value = ads.alert_read()
        voltage = ads.raw_to_v(value)
        print(f"Alert read: Raw={value}, Voltage={voltage:.6f}V")
        if value > threshold_high:
            print("High threshold exceeded!")
        elif value < threshold_low:
            print("Low threshold exceeded!")
        utime.sleep_ms(100)
    print()

def main():
    print("ADS1115 Test Script")
    print("==================")
    
    test_single_ended()
    test_differential()
    test_continuous_conversion()
    test_alert_mode()
    
    print("Test complete!")

if __name__ == "__main__":
    main()