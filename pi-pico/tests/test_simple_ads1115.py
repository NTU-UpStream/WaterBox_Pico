from machine import I2C, Pin
from ads1x15 import ADS1115

i2c=I2C(0, sda=Pin(4), scl=Pin(5))
adc = ADS1115(i2c, address=72, gain=1)
value = adc.read(0, 0)
print(value)