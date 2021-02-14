# MicroPython SSD1306 OLED driver, I2C and SPI interfaces
# Modifyed by Gary Metheringham with extra commands
#
#
# Availible Commands are:-
#
# poweroff()                             Turn of display
# poweron()                              Turn on display
# contrast(value)                        Set display contrast
# invert(0|1)                            Invert display 0=white on black / 1 black on white
# show()                                 Must be used to update the display
# scroll_in_screen(screen)               Scroll in a full screen horizontaly
# scroll_out_screen(screen)              Scroll out a full screen horizontaly
# scroll_screen_in_out(screen)           scrolls screen in and out horizontaly
# scroll_in_screen_v(screen)             Scroll in a full screen verticlay
# scroll_out_screen_v(screen)            Scroll out a full screen verticlay
# scroll_screen_in_out_v(screen)         scrolls screen in and out verticaly
# center(text, row)                      places text center justified
# left(text, row)                        places text left justified
# right(text, row)                       places test rught justified
# text(text, x, y)                       places text at position x, y
# pixel(x, y, 0|1)                       pixel at x, y, 0 off or 1 on
#
# note
# screen = [[x, y , screen_row1_text], [x, y, screen_row2_text], [x, y, screen1_row3_text], etc, etc]
    
from micropython import const
import framebuf

# register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.width > 2 * self.height else 0x12, # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL, 0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST, 0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)

    def scroll_in_screen(self,screen):
        self.screen = screen            
        for i in range (0, self.width+1, 4):
            for line in screen:
                self.text(line[2], -self.width+i, line[1])
                self.show()
            if i!= self.width:
                self.fill(0)

    # Scroll out screen horizontally from left to right    
    def scroll_out_screen(self,speed):
        self.speed = speed
        for i in range ((self.width+1)/self.speed):
            for j in range (self.height):
                self.pixel(i, j, 0)
                self.scroll(speed,0)
                self.show()

    # Continuous horizontal scroll
    def scroll_screen_in_out(self,screen):
        self.screen = screen            
        for i in range (0, (self.width+1)*2, 1):
            for line in screen:
                self.text(line[2], -self.width+i, line[1])
                self.show()
            if i!= self.width:
                self.fill(0)
    
    # Scroll in screen vertically 
    def scroll_in_screen_v(self,screen):
        self.screen = screen            
        for i in range (0, (self.height+1), 1):
            for line in screen:
                self.text(line[2], line[0], -self.height+i+line[1])
                self.show()
            if i!= self.height:
                self.fill(0)

    # Scroll out screen vertically 
    def scroll_out_screen_v(self,speed):
        self.speed = speed
        for i in range ((self.height+1)/speed):
            for j in range (self.width):
                self.pixel(j, i, 0)
                self.scroll(0,speed)
                self.show()

    # Continous vertical scroll
    def scroll_screen_in_out_v(self,screen):
        self.screen = screen
        for i in range (0, (self.height*2+1), 1):
            for line in screen:
                self.text(line[2], line[0], -self.height+i+line[1])
                self.show()
                if i!= self.height:
                    self.fill(0)
                    
    def center(self, txt, row):
        self.txt = txt
        self.lenght = len(self.txt)*8
        self.offset = int((self.width-self.lenght)/2)
        self.row = row
        self.text(txt, self.offset , row)

    def left(self, txt, row):
        self.txt = txt
        self.lenght = len(self.txt)*8
        self.offset = 0
        self.row = row
        self.text(txt, self.offset , row)

    def right(self, txt, row):
        self.txt = txt
        self.lenght = len(self.txt)*8
        self.offset = int((self.width-self.lenght))
        self.row = row
        self.text(txt, self.offset , row)







#
#
#
#
#
# set up display type I2C or SPI
#
#
#
#
class SSD1306_I2C(SSD1306):
    def __init__(self, i2c, width=128, height=64, addr=60, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)

    def autoaddr(self):
        for i in range(1, 127):
            try:
                if self.i2c.readfrom(i, 1):
                    return i
            except:
                pass
        raise Exception('I2C address detect error!')










# 
# class SSD1306_SPI(SSD1306):
#     def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
#         self.rate = 10 * 1024 * 1024
#         dc.init(dc.OUT, value=0)
#         res.init(res.OUT, value=0)
#         cs.init(cs.OUT, value=1)
#         self.spi = spi
#         self.dc = dc
#         self.res = res
#         self.cs = cs
#         import time
# 
#         self.res(1)
#         time.sleep_ms(1)
#         self.res(0)
#         time.sleep_ms(10)
#         self.res(1)
#         super().__init__(width, height, external_vcc)
# 
#     def write_cmd(self, cmd):
#         self.spi.init(baudrate=self.rate, polarity=0, phase=0)
#         self.cs(1)
#         self.dc(0)
#         self.cs(0)
#         self.spi.write(bytearray([cmd]))
#         self.cs(1)
# 
#     def write_data(self, buf):
#         self.spi.init(baudrate=self.rate, polarity=0, phase=0)
#         self.cs(1)
#         self.dc(1)
#         self.cs(0)
#         self.spi.write(buf)
#         self.cs(1)
