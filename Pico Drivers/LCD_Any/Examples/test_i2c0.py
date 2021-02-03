'''
    Liquid_Crystal_All
    By Gary Metheringham, 
            Modifyed from 
                    mpy drive for I2C LCD1602
                    by shaoziyang

    https://www.micropython.org

    LCD will auto detect first LCD Display if only using
    1 Display by omiting the last parameter (I2C Address)

    To Create an LCD Instance the format is

    Display = (I2C port, col=no. of columns, rows = no. of rows, addr = i2c device address)

    I2C Port = the i2c pinout port as setup in I2C module (usually 0)
    Columns = width of display (Usually 16 or 20)
    Rows = Height of display (Usually 2 or 4)
    addr = I2C device address default 63 (0x27)

    if Param columns is omitted default = 16
    if Param row is omitted default = 2
    if param address is omitted default = auto detect
'''
from machine import I2C, Pin
from Liquid_Crystal_i2c import LCD_MULTI
from time import sleep_ms



sda0 = Pin(0)
scl0 = Pin(1)

i2c0 = I2C(0, sda=sda0, scl=scl0, freq=400000)

print('i2c bus 0 found ')
print(i2c0.scan())

lcd1 = LCD_MULTI(i2c0,col=16,row=2)
lcd1.print('My address is ')
lcd1.print(i2c0.scan())

n = 1
x=0
while x==0:
    n+=1
    lcd1.printat(n,8,1)
    sleep_ms(750)
    