from machine import Pin,SPI,PWM
import binascii
import framebuf
import network
import socket
import time
import os
import uasyncio as asyncio

wlan = network.WLAN(network.STA_IF)

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

#32 to 126
char = 65
choice = 0
cursor = 0
line = 0
x = 55
y = 60
w = 38
l = 11

#ssid = ["T", "E", "S", "T"]
#passw = ["A", "A", "A", "A", "A", "A", "A", "A"]
ssid = ["A"]
passw = ["A"]

nl = []

ssidout = ""
passwout = ""

cont = True


class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 135

        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)

        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""
        self.rst(1)
        self.rst(0)
        self.rst(1)

        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35)

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F)

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)

        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x28)
        self.write_data(0x01)
        self.write_data(0x17)

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x35)
        self.write_data(0x00)
        self.write_data(0xBB)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

LCD = LCD_1inch14()

def connect_to_network(ss, pw):
    wlan.connect(ss, pw)

    max_wait = 30
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        clear()
        LCD.text("Connecting...",0,0,LCD.red)
        LCD.show()
        time.sleep(1)

    if wlan.status() != 3:
        clear()
        LCD.text("Network Connection Failed!!!",0,0,LCD.red)
        LCD.text("Network Connection Failed!!!",0,20,LCD.red)
        LCD.text("Network Connection Failed!!!",0,40,LCD.red)
        LCD.text("Network Connection Failed!!!",0,60,LCD.red)
        LCD.text("Network Connection Failed!!!",0,80,LCD.red)
        LCD.text("Network Connection Failed!!!",0,100,LCD.red)
        LCD.text("Network Connection Failed!!!",0,120,LCD.red)
        LCD.text("Network Connection Failed!!!",0,140,LCD.red)
        LCD.show()
        raise RuntimeError('network connection failed')
    else:
        clear()
        LCD.text("Connected!",0,0,LCD.green)
        status = wlan.ifconfig()
        LCD.text("IP Address: " + status[0],0,20,LCD.blue )
        LCD.show()

def clear():
    LCD.fill(LCD.white)

def getstring(dic):
    converted = str()
    for key in dic:
        converted += key
    return converted

if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535
    LCD.fill(LCD.white)
    LCD.show()
    keyA = Pin(15,Pin.IN,Pin.PULL_UP)
    keyB = Pin(17,Pin.IN,Pin.PULL_UP)

    keyUP = Pin(2 ,Pin.IN,Pin.PULL_UP)#UP
    keyCLICK = Pin(3 ,Pin.IN,Pin.PULL_UP)#CLICK
    keyLEFT = Pin(16 ,Pin.IN,Pin.PULL_UP)#LEFT
    keyDOWN = Pin(18 ,Pin.IN,Pin.PULL_UP)#DOWN
    keyRIGHT = Pin(20 ,Pin.IN,Pin.PULL_UP)#RIGHT

    wlan.active(True)
    wlan.config(pm = 0xa11140)

    while(cont == True):
        if line == 0 and choice == 1:
            networks = wlan.scan() # list with tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden
            i=0
            networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
            for wi in networks:
                if wi[0].decode() != "":
                    i+=1
                    nl.append(wi[0].decode())
            line = 1
            ssidout = nl[cursor]

        if(keyA.value() == 0):
            if line == 0:
                if x == 55:
                #Scan
                    choice = 1
                    x = 47
                    y = 0
                    l = 11
                    w = 11
                elif x == 142:
                #Manual
                    choice = 0
                    x = 47
                    y = 0
                    l = 11
                    w = 11
                    line = 1
            elif line == 1:
                ssid.append("A")
                char = 65
                cursor += 1
            elif line == 2:
                passw.append("A")
                char = 65
                cursor += 1
            time.sleep(.5)

        if(keyB.value() == 0):
            if line == 0:
                if x == 55:
                #Scan
                    pass
                elif x == 142:
                #Manual
                    pass
            elif line == 1:
                if cursor == len(ssid) - 1 and cursor != 0:
                    ssid.pop(cursor)
                    cursor -= 1
                    char = ord(ssid[cursor])
            elif line == 2:
                if cursor == len(passw) - 1 and cursor != 0:
                    passw.pop(cursor)
                    cursor -= 1
                    char = ord(passw[cursor])
            time.sleep(.25)

        if(keyUP.value() == 0):
            if line == 0:
                if x == 55:
                    #Scan
                    pass
                elif x == 142:
                    #Manual
                    pass
            elif line == 1 and choice == 0:
                if char < 126:
                    char += 1
                    ssid[cursor] = chr(char)               
            elif line == 1 and choice == 1:
                if cursor < len(nl) - 1:
                    cursor +=1
                    ssidout = nl[cursor]
            elif line == 2:
                if char < 126:
                    char += 1
                    passw[cursor] = chr(char)
            time.sleep(.25)

        if(keyDOWN.value() == 0):
            if line == 0:
                if x == 55:
                #Scan
                    pass
                elif x == 142:
                #Manual
                    pass
            elif line == 1 and choice == 0:
                if char > 31:
                    char -= 1
                    ssid[cursor] = chr(char)
            elif line == 1 and choice == 1:
                if cursor != 0:
                    cursor -=1
                    ssidout = nl[cursor]
            elif line == 2:
                if char > 31:
                    char -= 1
                    passw[cursor] = chr(char)
            time.sleep(.25)

        if(keyCLICK.value() == 0):
            if line == 0:
                if x == 55:
                #Scan
                    pass
                elif x == 142:
                #Manual
                    pass
            elif line == 1:
                cursor = 0
                line = 2
                char = 65
                x = 78
                y = 18
            elif line == 2:
                cont = False
                connect_to_network(ssidout, passwout)
            time.sleep(.5)

        if(keyLEFT.value() == 0):
            if line == 0:
                if x == 55:
                    #Scan
                    x = 142
                    w = 55
                elif x == 142:
                    #Manual
                    x = 55
                    w = 38
            elif line == 1 and choice == 0:
                if cursor > 0:
                    cursor -= 1
                    char = ord(ssid[cursor])
            elif line == 2:
                if cursor > 0:
                    cursor -= 1
                    char = ord(passw[cursor])
            time.sleep(.25)

        if(keyRIGHT.value() == 0):
            if line == 0:
                if x == 55:
                    #Scan
                    x = 142
                    w = 55
                elif x == 142:
                    #Manual
                    x = 55
                    w = 38
            elif line == 1:
                if cursor < len(ssid) - 1:
                    cursor += 1
                    char = ord(ssid[cursor])
            elif line == 2:
                if cursor < len(passw) - 1:
                    cursor += 1
                    char = ord(passw[cursor])
            time.sleep(.25)

        if cont == True:
            if line > 0:
                clear()
                if choice == 0:
                    ssidout = getstring(ssid)
                passwout = getstring(passw)
                LCD.text("SSID: " + ssidout,0,0,LCD.blue)
                LCD.text("Password: " + passwout,0,20,LCD.green)
                newpos = cursor * 8
                if line == 1 and choice == 0:
                    x = 47 + newpos
                elif line == 2:
                    x = 79 + newpos
                LCD.rect(x,y,w,l,LCD.red)
                LCD.show()
            else:
                clear()
                LCD.text("Select an option:",58,42,LCD.red)
                LCD.text("Scan",58,62,LCD.blue)
                LCD.text("Manual",145,62,LCD.blue)
                LCD.rect(x,y,w,l,LCD.red)
                LCD.show()
    time.sleep(1)
    LCD.fill(0xFFFF)
