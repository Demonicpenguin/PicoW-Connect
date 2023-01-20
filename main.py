from machine import Pin,SPI,PWM
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

cursor = 0
line = 1

x = 47
y = 0
l = 11
w = 11

ssid = ["T", "E", "S", "T"]
passw = ["A", "A", "A", "A", "A", "A", "A", "A"]

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
    wlan.active(True)
    wlan.config(pm = 0xa11140)
    wlan.connect(ss, pw)

    max_wait = 10
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
    
def increment(cur):
    if cur == "A":
        return "B"
    elif cur == "B":
        return "C"
    elif cur == "C":
        return "D"
    elif cur == "D":
        return "E"
    elif cur == "E":
        return "F"
    elif cur == "F":
        return "G"
    elif cur == "G":
        return "H"
    elif cur == "H":
        return "I"
    elif cur == "I":
        return "J"
    elif cur == "J":
        return "K"
    elif cur == "K":
        return "L"
    elif cur == "L":
        return "M"
    elif cur == "M":
        return "N"
    elif cur == "N":
        return "O"
    elif cur == "O":
        return "P"
    elif cur == "P":
        return "Q"
    elif cur == "Q":
        return "R"
    elif cur == "R":
        return "S"
    elif cur == "S":
        return "T"
    elif cur == "T":
        return "U"
    elif cur == "U":
        return "V"
    elif cur == "V":
        return "W"
    elif cur == "W":
        return "X"
    elif cur == "X":
        return "Y"
    elif cur == "Y":
        return "Z"
    elif cur == "Z":
        return "1"
    elif cur == "1":
        return "2"
    elif cur == "2":
        return "3"
    elif cur == "3":
        return "4"
    elif cur == "4":
        return "5"
    elif cur == "5":
        return "6"
    elif cur == "6":
        return "7"
    elif cur == "7":
        return "8"
    elif cur == "8":
        return "9"
    elif cur == "9":
        return "0"
    elif cur == "0":
        return "!"
    elif cur == "!":
        return "@"
    elif cur == "@":
        return "#"
    elif cur == "#":
        return "%"
    elif cur == "%":
        return "^"
    elif cur == "^":
        return "&"
    elif cur == "&":
        return "*"
    elif cur == "*":
        return "("
    elif cur == "(":
        return ")"
    elif cur == ")":
        return "-"
    elif cur == "-":
        return "="
    elif cur == "=":
        return "_"
    elif cur == "_":
        return "{"
    elif cur == "{":
        return "}"
    elif cur == "}":
        return "|"
    elif cur == "|":
        return ":"
    elif cur == ":":
        return ";"
    elif cur == ";":
        return "'"
    elif cur == "'":
        return ","
    elif cur == ",":
        return "<"
    elif cur == "<":
        return "."
    elif cur == ".":
        return ">"
    elif cur == ">":
        return "/"
    elif cur == "/":
        return " "
    elif cur == " ":
        return "A"

def decrement(cur):
    if cur == "A":
        return " "
    elif cur == "B":
        return "A"
    elif cur == "C":
        return "B"
    elif cur == "D":
        return "C"
    elif cur == "E":
        return "D"
    elif cur == "F":
        return "E"
    elif cur == "G":
        return "F"
    elif cur == "H":
        return "G"
    elif cur == "I":
        return "H"
    elif cur == "J":
        return "I"
    elif cur == "K":
        return "J"
    elif cur == "L":
        return "K"
    elif cur == "M":
        return "L"
    elif cur == "N":
        return "M"
    elif cur == "O":
        return "N"
    elif cur == "P":
        return "O"
    elif cur == "Q":
        return "P"
    elif cur == "R":
        return "Q"
    elif cur == "S":
        return "R"
    elif cur == "T":
        return "S"
    elif cur == "U":
        return "T"
    elif cur == "V":
        return "U"
    elif cur == "W":
        return "V"
    elif cur == "X":
        return "W"
    elif cur == "Y":
        return "X"
    elif cur == "Z":
        return "Y"
    elif cur == "1":
        return "Z"
    elif cur == "2":
        return "1"
    elif cur == "3":
        return "2"
    elif cur == "4":
        return "3"
    elif cur == "5":
        return "4"
    elif cur == "6":
        return "5"
    elif cur == "7":
        return "6"
    elif cur == "8":
        return "7"
    elif cur == "9":
        return "8"
    elif cur == "0":
        return "9"
    elif cur == "!":
        return "0"
    elif cur == "@":
        return "!"
    elif cur == "#":
        return "@"
    elif cur == "%":
        return "#"
    elif cur == "^":
        return "%"
    elif cur == "&":
        return "^"
    elif cur == "*":
        return "&"
    elif cur == "(":
        return "*"
    elif cur == ")":
        return "("
    elif cur == "-":
        return ")"
    elif cur == "=":
        return "-"
    elif cur == "_":
        return "="
    elif cur == "{":
        return "_"
    elif cur == "}":
        return "{"
    elif cur == "|":
        return "}"
    elif cur == ":":
        return "|"
    elif cur == ";":
        return ":"
    elif cur == "'":
        return ";"
    elif cur == ",":
        return "'"
    elif cur == "<":
        return ","
    elif cur == ".":
        return "<"
    elif cur == ">":
        return "."
    elif cur == "/":
        return ">"
    elif cur == " ":
        return "/"
    
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
    
    keyUP = Pin(2 ,Pin.IN,Pin.PULL_UP)
    keyCLICK = Pin(3 ,Pin.IN,Pin.PULL_UP)
    keyLEFT = Pin(16 ,Pin.IN,Pin.PULL_UP)
    keyDOWN = Pin(18 ,Pin.IN,Pin.PULL_UP)
    keyRIGHT = Pin(20 ,Pin.IN,Pin.PULL_UP)
    
    while(cont == True):
        if(keyA.value() == 0):
            if line == 1:
                cursor = 0
                line = 2
                x = 78
                y = 18
            elif line == 2:
                cont = False                
                connect_to_network(ssidout, passwout)
            time.sleep(.5)
            
        if(keyB.value() == 0):      
            if line == 1:
                if ssid[cursor].islower():
                    if cursor == len(ssid) - 1 and cursor != 0:
                        ssid.pop(cursor)
                        cursor -= 1
                    else:
                        ssid[cursor] = ssid[cursor].upper()
                else:
                    ssid[cursor] = ssid[cursor].lower()
            elif line == 2:
                if passw[cursor].islower():
                    if cursor == len(passw) - 1 and cursor != 0:
                        passw.pop(cursor)
                        cursor -= 1
                    else:
                        passw[cursor] = passw[cursor].upper()
                else:
                    passw[cursor] = passw[cursor].lower()
            time.sleep(.25)

        if(keyUP.value() == 0):
            if line == 1:
                ssid[cursor] = increment(ssid[cursor].upper())
            elif line == 2:
                passw[cursor] = increment(passw[cursor].upper())
            time.sleep(.25)
            
        if(keyCLICK.value() == 0):
            if line == 1:
                ssid.append("A")
            elif line == 2:
                passw.append("A")
            cursor += 1
            time.sleep(.5)
            
        if(keyLEFT.value() == 0):
            if line == 1:
                if cursor > 0:
                    cursor -= 1
            elif line == 2:
                if cursor > 0:
                    cursor -= 1
            time.sleep(.25)
            
        if(keyDOWN.value() == 0):
            if line == 1:
                ssid[cursor] = decrement(ssid[cursor].upper())
            elif line == 2:                
                passw[cursor] = decrement(passw[cursor].upper())
            time.sleep(.25)
            
        if(keyRIGHT.value() == 0):
            if line == 1:
                if cursor < len(ssid) - 1:
                    cursor += 1
            elif line == 2:
                if cursor < len(passw) - 1:
                    cursor += 1
            time.sleep(.25)
            
        if cont == True:
            clear()
            ssidout = getstring(ssid)
            passwout = getstring(passw)
            LCD.text("SSID: " + ssidout,0,0,LCD.blue)
            LCD.text("Password: " + passwout,0,20,LCD.green)
            newpos = cursor * 8
            if line == 1:
                x = 47 + newpos
            else:
                x = 79 + newpos
            LCD.rect(x,y,l,w,LCD.red)
            LCD.show()
    time.sleep(1)
    LCD.fill(0xFFFF)



