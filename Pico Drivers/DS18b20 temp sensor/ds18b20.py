import time
import machine
import onewire, ds18x20
import ssd1306n
from machine import I2C
# the device is on GPIO12
dat = machine.Pin(12)
i2c = I2C(0)
oled = ssd1306n.SSD1306_I2C(i2c)
oled.fill(0)
# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))
import array, time
from machine import Pin
import rp2
 
# Configure the number of WS2812 LEDs, pins and brightness.
NUM_LEDS = 50
PIN_NUM = 16
brightness = 0.1
 
 
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
 
 
# Create the StateMachine with the ws2812 program, outputting on Pin(16).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
 
# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)
 
# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])
 
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)
 
def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]
 
def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)
 
 
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)
 
 

# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)
temp = 0
tmp = 0
high = -999
low = 999

# loop 10 times and print all temperatures
while(1):
    print('temperatures:',temp,tmp, end=' ')
    oled.fill(0)
    oled.text("  temperature ", 0, 1)
    oled.text(str(temp), 30, 15)
    oled.text("Max",5,35)
    oled.text(str(high),50,35)
    oled.text("Min",5,50)
    oled.text(str(low),50,50)
    oled.show()
    ds.convert_temp()
    time.sleep_ms(2000)
    for rom in roms:
        temp=(ds.read_temp(rom))
        tmp= int(temp/2)
        if temp >high: high = temp
        if temp <low: low = temp
        if temp > 0:
            
            for led in range(0,tmp):
                colour = GREEN
                pixels_set(led, colour)
                
        if temp < 1:
            tmp = tmp *-1
            for led in range(0,tmp):
                colour = BLUE
                pixels_set(led, colour)
        for led in range((tmp+1), NUM_LEDS):
            colour = BLACK
            pixels_set(led, colour)
                
        pixels_show()
        
    print()
    