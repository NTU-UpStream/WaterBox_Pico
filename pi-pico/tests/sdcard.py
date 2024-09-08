import uos
from machine import Pin, SPI
from sdcard import SDCard
import time
import sys

SD_SCK = 18
SD_CS = 17
SD_MOSI = 19
SD_MISO = 16

power = Pin(6, Pin.OUT)
power.on()
spi = SPI(0)
sdcard = SDCard(SPI(0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), Pin(SD_CS))
storage = uos.VfsFat(sdcard)

print("Mounting Filesystem.")
uos.mount(storage, "/sd")
print("Mounting succesfully.")


print("Current file system.")
print(uos.listdir("/"))

print("Writing data to dummy file.")
f = open("/sd/sdtest", "w")
f.write("Testing SDCard")
f.close()

print("Current 'sd' file system.")
print(uos.listdir("/sd/"))

print("Reading data from dummy file.")
f = open("/sd/sdtest", "r")
data = f.readline()
if data != "Testing SDCard":
    print("Readed data is not as same as expected. SD card might be broken.")
print(data)