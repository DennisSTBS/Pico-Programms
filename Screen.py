from machine import SPI, Pin, I2C
from time import sleep
import time
import alphabetBitmap as ab

############################## DEFINITIONS ##############################

CONST_BLACK = 0x0000
CONST_GREY = 0x5555
CONST_BLUE = 0x001F
CONST_RED = 0xF800
CONST_GREEN = 0x07E0
CONST_CYAN = 0x07FF
CONST_MAGENTA = 0xF81F
CONST_YELLOW = 0xFFE0
CONST_WHITE = 0xFFFF

CONST_BG_COLOR = CONST_BLACK

CHAR_SIZE = 2
GRAPH_SIZE = 1

################################## LCD ##################################
en = Pin(0, Pin.OUT, value=1)
cs = Pin(1, Pin.OUT, value=0)
dc = Pin(5, Pin.OUT, value=0)

spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))

spi.write(bytes([0xAF]))  # disable sleep
spi.write(bytes([0xA5]))  # full white
time.sleep(0.5)
spi.write(bytes([0xA4]))  # full black

# 96x96 white (full screen)
spi.write(bytes([0x15]))  # set x for write to 0-95
dc.on()  # enable DC for parameters
spi.write(bytes([0+16, 95+16]))
dc.off() # disable DC for next command

spi.write(bytes([0x75]))  # set y for write to 0-95
dc.on()
spi.write(bytes([0, 95]))
dc.off()

spi.write(bytes([0x5C]))  # write 96x96
dc.on()
spi.write(bytes([0xff]*2*96*96))
dc.off()

spi.write(bytes([0xA6]))  # display
#spi.write(bytes([0xAE]))  # enable sleep
#cs.off()
#time.sleep(5)
#en.off()

################################## DHT20 ##################################

MBE280_ADDR = 0x38
i2c = I2C(1, sda=Pin(6), scl=Pin(7)) 

globalOffset = 16

xPlot = 0

def GetReadings():
    i2c.writeto(MBE280_ADDR, bytes([0x71]))
    sleep(0.5)
    i2c.writeto(MBE280_ADDR, bytes([0xAC]))
    sleep(0.5)
    data = bytearray(i2c.readfrom_mem(MBE280_ADDR, 0x38, 8))
    return data

def GetHumidity(data : bytes):
    humidity = ((data[1] << 12) + ((data[2] << 4) + data[3] >> 4))
    return (humidity / pow(2,20)) * 100

def GetTemperature(data : bytes):
    temperature = ((data[3]&15) << 16) + (data[4] << 8) + data[5]
    return (temperature / pow(2,20)) * 200 - 50

################################## HELPERS ##################################

def ClearScreen():
    print("Clear Screen")
    spi.write(bytes([0x15]))  # set x
    dc.on()
    spi.write(bytes([0+globalOffset, 96+globalOffset]))
    dc.off()

    spi.write(bytes([0x75]))  # set y
    dc.on()
    spi.write(bytes([0, 96]))
    dc.off()

    spi.write(bytes([0x5C])) # write
    dc.on()
    color = CONST_BG_COLOR
    spi.write(color.to_bytes(2, "big")*97*97)
    dc.off()
    return

def DrawBox(x1, y1, x2, y2, color):
    xsize = x2-x1 + 1
    ysize = y2-y1 + 1
    spi.write(bytes([0x15]))  # set x
    dc.on()
    spi.write(bytes([x1+globalOffset, x2+globalOffset]))
    dc.off()

    spi.write(bytes([0x75]))  # set y
    dc.on()
    spi.write(bytes([y1, y2]))
    dc.off()

    spi.write(bytes([0x5C])) # write
    dc.on()
    spi.write(color.to_bytes(2, "big")*xsize*ysize)
    dc.off()
    return

def DrawGraph(xPlot, data, color):
    spi.write(bytes([0xAF]))  # disable sleep

    spi.write(bytes([0x15]))  # set x
    dc.on()
    spi.write(bytes([globalOffset+xPlot, globalOffset+xPlot+1]))
    dc.off()

    spi.write(bytes([0x75]))  # set y
    dc.on()
    spi.write(bytes([data, data+1]))
    dc.off()

    spi.write(bytes([0x5C])) # write
    dc.on()
    spi.write(color.to_bytes(2, "big")*GRAPH_SIZE*GRAPH_SIZE)
    dc.off()

    spi.write(bytes([0xA6]))  # display
    cs.off()
    return

def DrawDottedLine(lineHeight = 10, lineLength = 5, color = CONST_BLACK):
    lineMax = 95 / lineLength

    for i in range(1, int(lineMax)):
        if((i % 2) == 0):
            DrawBox(lineLength*(i-1), lineHeight, lineLength*i, lineHeight, color)

def DrawYDottedLines(color):
    for i in range(1, 10):
        DrawDottedLine(i*10, 3, color)

def DrawCharacter(offsetX, offsetY, character, color, characterSize):
    offsetY = offsetY-5*characterSize-1
    spi.write(bytes([0x15]))  # set x
    dc.on()
    spi.write(bytes([globalOffset + offsetX, globalOffset + offsetX + 5*characterSize-1]))
    dc.off()

    spi.write(bytes([0x75]))  # set y
    dc.on()
    spi.write(bytes([offsetY, offsetY + 5*characterSize-1]))
    dc.off()

    spi.write(bytes([0x5C])) # write
    dc.on()

    for line in character:
        for i in range(characterSize):
            for char in line:
                if(char == 1):
                    spi.write(color.to_bytes(2, "big")*characterSize)
                else:
                    spi.write(CONST_BG_COLOR.to_bytes(2, "big")*characterSize)
    dc.off()
    return

def DrawMultipleCharacters(offsetX : int, offsetY : int, characters: list[int], color : int, characterSize = 1):
    offsetY += 6 * CHAR_SIZE

    for char in characters:
        DrawCharacter(offsetX, offsetY, char, color, characterSize)
        offsetX += 5 * CHAR_SIZE + 1
    return

def NumberToBitmapDict(number):
    number = str(number)
    bitMapDict = []
    for letter in number:
        bitMapDict.append(ab.numbers[letter])
    return bitMapDict

############################ MAIN #############################

DrawBox(0, 0, 96, 96, CONST_BG_COLOR)
DrawYDottedLines(CONST_GREY)

data = GetReadings()
humidity = GetHumidity(data)
temperature = GetTemperature(data)

DrawCharacter(0, int(temperature), ab.numbers["°"], CONST_RED, CHAR_SIZE)       # Draw Celsius
DrawCharacter(0, int(humidity), ab.numbers["%"], CONST_BLUE, CHAR_SIZE)         # Draw Percent

while(True):
    data = GetReadings()
    humidity = GetHumidity(data)
    temperature = GetTemperature(data)

    print("Humidity: {}".format(humidity))
    print("Temperature: {} \n".format(temperature))

    DrawGraph(xPlot, int(temperature), CONST_RED)
    DrawMultipleCharacters(76, 0, NumberToBitmapDict(int(temperature)), CONST_RED, CHAR_SIZE)
    DrawGraph(xPlot, int(humidity), CONST_BLUE)
    DrawMultipleCharacters(0, 0, NumberToBitmapDict(int(humidity)), CONST_BLUE, CHAR_SIZE)

    if(xPlot>=96):
        xPlot = 0
        ClearScreen()
        DrawYDottedLines(CONST_GREY)
        DrawMultipleCharacters(0, 0, NumberToBitmapDict(int(humidity)), CONST_BLUE, CHAR_SIZE)      # Draw Humidity
        DrawMultipleCharacters(76, 0, NumberToBitmapDict(int(temperature)), CONST_RED, CHAR_SIZE)   # Draw Temperature
        DrawCharacter(0, int(temperature), ab.numbers["°"], CONST_RED, CHAR_SIZE)                   # Draw Celsius °
        DrawCharacter(0, int(humidity), ab.numbers["%"], CONST_BLUE, CHAR_SIZE)                     # Draw Percent %
    xPlot += 1
