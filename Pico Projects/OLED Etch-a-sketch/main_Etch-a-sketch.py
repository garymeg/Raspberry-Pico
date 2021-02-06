from math import *
from machine import *
import ssd1306n
import gfx
import machine
import time
import uos
from machine import Pin, I2C, ADC
i2c0_avail = 1 
i2c1_avail = 0

scl1 = Pin(5)
sda1 = Pin(4)
scl2 = Pin(19)
sda2 = Pin(18)
vert = ADC(0)
hors = ADC(1)
clr = Pin(9, Pin.IN)

print(uos.uname())
print("Freq: "  + str(machine.freq()) + " Hz")
print("128x64 SSD1306 I2C OLED on Raspberry Pi Pico")

if i2c0_avail :
    i2c1 = I2C(0, scl= scl1, sda= sda1, freq= 2000000)
    print("Available i2c 1st BUS devices: "+ str(i2c1.scan()))
    oled1 = ssd1306n.SSD1306_I2C(i2c1)
    oled1.fill(0)
    graphics1 = gfx.GFX(oled1.pixel,128,64)
    
if i2c1_avail :
    i2c2 = I2C(1, scl= scl2, sda= sda2, freq= 2000000)
    print("Available i2c 2nd BUS devices: "+ str(i2c2.scan()))
    oled2 = ssd1306n.SSD1306_I2C(i2c2,addr=60)
    oled2.fill(0)
    graphics2 = gfx.GFX(oled2.pixel, 128, 64)
    
if i2c0_avail:
    n = 1
    x1 = 1
    while n==1:
                  
        
            y = int((64/655)*ADC.read_u16(hors)/100)
            x = int((127/655)*ADC.read_u16(vert)/100)
            oled1.pixel(x,y,1)
            if clr.value() == 1:
                oled1.fill(0)
            print(x,y)
            oled1.show()
            