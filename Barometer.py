from machine import I2C, Pin
import time

MBE280_ADDR = 0x77

# Initialisierung I2C
i2c = I2C(1, sda=Pin(6), scl=Pin(7)) 

# I2C-Bus-Scan ausgeben
print(i2c.scan())

data = i2c.readfrom_mem(MBE280_ADDR, 0, 10)

for entry in data:
    print("{}".format(entry))
