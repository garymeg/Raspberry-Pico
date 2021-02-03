'''
    I2C LCD1602 demo

    Author: shaoziyang
    Date:   2018.2

    http://www.micropython.org.cn

'''
import machine
from machine import I2C, Pin
from mp_i2c_lcd1602 import LCD1602
import time
from time import sleep_ms

sda01 = machine.Pin(0)
scl01 = machine.Pin(1)
scl11 = machine.Pin(19)
sda11 = machine.Pin(18)

i2c01 = I2C(0, sda=sda01, scl=scl01)
i2c11 = I2C(1, sda=sda11, scl=scl11)
print(i2c01.scan())
print(i2c11.scan())

LCD01 = LCD1602(i2c01, 63)
LCD11 = LCD1602(i2c11, 63)

LCD01.puts("Calculation time")
LCD11.puts("fibonacci numbers")
n = 0
seq = 1
nfib = 1
ofib = 0


def fibno(new,old):
    a = old
    old = new
    start = time.ticks_us()
    nfib = new+a
    diff = time.ticks_diff(time.ticks_us(), start)
    
    return (nfib,old, diff)
old = 0
new = 1
while 1:
    n = new
    o = old
    new, old, diff = fibno(n, o)
    LCD01.puts(chr(228)+'s',0,1)
    LCD01.puts(diff, 3, 1)
    LCD01.puts('seq',7,1)
    LCD11.puts(new, 0, 1)
    LCD01.puts(seq, 12,1)
    seq += 1
    sleep_ms(500)
    

