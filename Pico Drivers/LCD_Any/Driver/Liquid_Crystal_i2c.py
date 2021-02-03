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
from utime import sleep_ms
from machine import I2C


LCD_I2C_ADDR=(63)

class LCD_MULTI():
    def __init__(self, i2c, col = 16, row = 2, addr = 0):
        self.i2c=i2c
        self.buf = bytearray(1)
        self.BK, self.RS, self.E = 0x08, 0x00, 0x04
        self.ADDR = addr if addr else self.autoaddr()
        self.COL = col
        self.ROW = row
        self.setcmd(0x33)
        sleep_ms(5)
        self.send(0x30)
        sleep_ms(5)
        self.send(0x20)
        sleep_ms(5)
        for i in [0x28, 0x0C, 0x06, 0x01]:
            self.setcmd(i)
        self.px, self.py = 0, 0
        self.pb = bytearray(' '*self.COL)
        self.version='2.0'

    def setReg(self, dat):
        self.buf[0] = dat
        self.i2c.writeto(self.ADDR, self.buf)
        sleep_ms(1)

    def send(self, dat):
        d=(dat&0xF0)|self.BK|self.RS
        self.setReg(d)
        self.setReg(d|0x04)
        self.setReg(d)

    def setcmd(self, cmd):
        self.RS=0
        self.send(cmd)
        self.send(cmd<<4)

    def setdat(self, dat):
        self.RS=1
        self.send(dat)
        self.send(dat<<4)

    def autoaddr(self):
        for i in range (126):
            try:
                if self.i2c.readfrom(i, 1):
                    return i
            except:
                pass
        raise Exception('I2C address detect error!')

    def clear(self):
        self.setcmd(1)

    def backlight(self, on):
        if on:
            self.BK=0x08
        else:
            self.BK=0
        self.setcmd(0)

    def on(self):
        self.setcmd(0x0C)

    def off(self):
        self.setcmd(0x08)

    def shl(self):
        self.setcmd(0x18)

    def shr(self):
        self.setcmd(0x1C)

#0x80 is line 1
#0xbf is line 2
#0x93 is line 3
#0xd3 is line 4
        #sends start of each lcd line memory location to lcd depending on what line were on 
    def char(self, ch, x=-1, y=0):
        if x>=0:
            a=0x80  #if were on line 0 then set cursor to start of lcd line 0
            if y>0:
                a=0xc0   #if were on line 1 then set cursor to start of lcd line 1
                if y>1:
                    a=0x94 #if were on line 2 then set cursor to start of lcd line 2
                    if y>2:
                        a=0xd4 #if were on line 3 then set cursor to start of lcd line 3
            self.setcmd(a+x)
        self.setdat(ch)

    def printat(self, s, x=0, y=0):
        if type(s) is not str:
            s = str(s)
        if len(s)>0:
            self.char(ord(s[0]),x,y)
            for i in range(1, len(s)):
                self.char(ord(s[i]))

    def newline(self):
        self.px = 0
        if self.py < self.ROW-1:
            self.py += 1
        else:
            for i in range(self.ROW-1):
                self.char(self.pb[i], i)
                self.char(32, i, 1)
                self.pb[i] = 32

    def print(self, s):
        if type(s) is not str:
            s = str(s)
        for i in range(len(s)):
            d = ord(s[i])
            if d == ord('\n'):
                self.newline()
            else:
                self.char(d, self.px, self.py)
                if self.py:
                    self.pb[self.px] = d
                self.px += 1
                if self.px > (self.COL-1):
                    self.newline()
                
                    
                    