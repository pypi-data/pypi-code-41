

import struct
import spidev
import RPi.GPIO as GPIO
import time
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 300000

""" String to List of Hexa decimal conversion"""
""" call bytearray('234.5') in the list"""
class StrtoHexList(list):
	def __repr__(self):
		return '['+','.join("0x%X"%x if type(x) is int else repr(x) for x in self)+']'

class bytestofloat:
        def __init__(self, byte):
                List = byte
                List.reverse()
                Join_Chars = ''.join(chr(i) for i in List)
                #print (Join_Chars)
                self.Float = struct.unpack(">f", bytes(Join_Chars, 'latin-1'))

class SETTransactions:
        def __init__(self, Register, Data, ChipSelect, Interrupt):
                """
                Can be used with commands SET_Rset, SET_Rmax, SET_Mode and TEST_CMD
                """
                to_send = StrtoHexList(bytearray(Data, 'ascii'))
                #print (to_send)
                GPIO.output(ChipSelect, 0)
                Dummy1 = spi.xfer2([Register])
                Dummy2 = spi.xfer2(to_send)
                Dummy3 = spi.xfer2([0X2A])
                GPIO.output(ChipSelect, 1)
                self.Received = []
                time.sleep(0.005)
                while GPIO.input(Interrupt):
                        GPIO.output(ChipSelect, 0)
                        x = spi.readbytes(1)
                        GPIO.output(ChipSelect, 1)
                        self.Received.append(x[0])
                        time.sleep(0.00002)         # Sleep functionality used

class GETTransactions:
        def __init__(self, Register, ChipSelect, Interrupt):
                """
                Can be used with rest all commands
                """

                GPIO.output(ChipSelect, 0)
                Dummy4 = (spi.xfer2([Register]))
                Dummy5 = (spi.xfer2([0X2A]))
                if Dummy4[0] > 127:
                        self.Alarm = 1
                else:
                        self.Alarm = 0
                #time.sleep(0.002)                    # Sleep functionality used
                GPIO.output(ChipSelect, 1)
                self.Received = []
                time.sleep(0.005)
                
                #print (GPIO.input(Interrupt))
                while GPIO.input(Interrupt):
                        GPIO.output(ChipSelect, 0)
                        x = spi.readbytes(1)
                        GPIO.output(ChipSelect, 1)
                        self.Received.append(x[0])
                        time.sleep(0.00002)         # Sleep functionality used
                    
                if len(self.Received)==4:
                        #print (self.Received)
                        self.Float = bytestofloat(self.Received)
                        
                if len(self.Received)==3: # for Dual Heater
                        #print (self.Received)
                        self.Float = self.Received[2]+self.Received[1]*255+self.Received[0]*255*255

                elif len(self.Received)==1:
                        #print ("1 byte received")
                        self.Character = chr(self.Received[0])

                elif len(self.Received) > 5:
                        #print (self.Received)
                        self.String = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])
                        #spi.close()

                elif len(self.Received)==5:
                        #print ("5 byte received")
                        self.Version = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])


                        
                        
