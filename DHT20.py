from machine import I2C, Pin, UART
from time import sleep

MBE280_ADDR = 0x38

# UART erstellen
uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# Initialisierung I2C
i2c = I2C(1, sda=Pin(6), scl=Pin(7)) 

# I2C-Bus-Scan ausgeben
print(i2c.scan())


def get_reading():
    i2c.writeto(MBE280_ADDR, bytes([0x71]))
    sleep(0.1)
    i2c.writeto(MBE280_ADDR, bytes([0xAC]))
    sleep(0.1)
    data = bytearray(i2c.readfrom_mem(MBE280_ADDR, 0x38, 8))
    return data

def GetHumidity(data : bytes):
    humidity = ((data[1] << 12) + ((data[2] << 4) + data[3] >> 4))
    return humidity

def GetTemperature(data : bytes):
    temperature = ((data[3]&15) << 16) + (data[4] << 8) + data[5]
    return temperature

def HumidityConversion(relativeHumiditySignal : float):
    return (relativeHumiditySignal / pow(2,20)) * 100

def TemperatureConversion(temperature : float):
    return (temperature / pow(2,20)) * 200 - 50

while(True):
    uart1.write(b"hello")  # write 5 bytes
    data = get_reading()
    print("Humidity: {}".format(HumidityConversion(GetHumidity(data))))
    print("Temperature: {} \n".format(TemperatureConversion(GetTemperature(data))))
    #sleep(0.1)
