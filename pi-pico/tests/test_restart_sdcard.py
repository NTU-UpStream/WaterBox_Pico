from machine import Pin
from sdcard import SDCard
from storage import Storage
import uos
import time

power = Pin(6, Pin.OUT)
power.on()

storage = Storage()
storage.mount()

file = open('/sdcard/test.txt', 'w')
file.write('Hello World Sdcard.')
file.close()

power.off()
time.sleep(1)
power.on()

storage.mount()

file = open('/sdcard/test.txt', 'r')
print(file.read())
file.close()
