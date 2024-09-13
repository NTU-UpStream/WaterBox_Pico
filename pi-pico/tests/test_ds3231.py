from machine import I2C, Pin
from ds3231 import DS3231, TEMPERATURE_REG
import utime

# Power up ADS1115
power = Pin(6, Pin.OUT)
power.on()
utime.sleep(1)

# Initialize I2C
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=40000)

# Initialize DS3231
rtc = DS3231(i2c)

def test_set_and_read_time():
    print("Testing set and read time:")
    # Set the time to 2023-09-12 15:30:00 (Tuesday)
    rtc.datetime((2023, 9, 12, 15, 30, 0, 2))
    utime.sleep(2)
    current_time = rtc.datetime()
    print(f"Current time: {current_time}")

def test_alarms():
    print("\nTesting alarms:")
    # Set Alarm 1 to trigger every minute
    rtc.alarm1((0,), match=rtc.AL1_MATCH_S)
    print("Alarm 1 set to trigger every minute")

    # Set Alarm 2 to trigger at 15:31
    rtc.alarm2((31, 15), match=rtc.AL2_MATCH_HM)
    print("Alarm 2 set to trigger at 15:31")

    # Wait and check alarms
    for _ in range(5):
        utime.sleep(30)
        if rtc.check_alarm(1):
            print("Alarm 1 triggered!")
        if rtc.check_alarm(2):
            print("Alarm 2 triggered!")

def test_square_wave():
    print("\nTesting square wave output:")
    # Enable 1Hz square wave output
    rtc.square_wave(rtc.FREQ_1)
    print("1Hz square wave enabled")
    utime.sleep(5)

    # Disable square wave output
    rtc.square_wave(False)
    print("Square wave disabled")

def test_temperature():
    print("\nTesting temperature reading:")
    # Read temperature (assuming the DS3231 supports this feature)
    temp_reg = i2c.readfrom_mem(rtc.addr, TEMPERATURE_REG, 2)
    temp = temp_reg[0] + (temp_reg[1] >> 6) * 0.25
    print(f"Current temperature: {temp}°C")

def main():
    print("DS3231 RTC Test Script")
    print("=====================")

    test_set_and_read_time()
    test_temperature()

    print("\nTest complete!")

if __name__ == "__main__":
    main()