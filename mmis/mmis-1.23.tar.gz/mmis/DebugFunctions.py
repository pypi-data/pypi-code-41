

import struct
import spidev
import RPi.GPIO as GPIO
import time
spi = spidev.SpiDev()
spi.open(0,0)
#spi.max_speed_hz = 50000
#GPIO.setmode(GPIO.BOARD)

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
                GPIO.output(ChipSelect, 0)
                Dummy1 = spi.xfer2([Register])
                Dummy2 = spi.xfer2(to_send)
                Dummy3 = spi.xfer2([0X2A])
                GPIO.output(ChipSelect, 1)
                self.Received = []
                while GPIO.input(Interrupt):
                        GPIO.output(ChipSelect, 0)
                        x = spi.readbytes(1)
                        GPIO.output(ChipSelect, 1)
                        self.Received.append(x[0])
                        time.sleep(0.00002)         # Sleep functionality used

class GETTransactions:
        def __init__(self, Register, ChipSelect, Interrupt, wait_time):
                """
                Can be used with rest all commands
                """
                GPIO.output(ChipSelect, 0)
                Dummy1 = spi.xfer2([Register])
                Dummy2 = spi.xfer2([0X2A])
                time.sleep(0.002)                    # Sleep functionality used
                GPIO.output(ChipSelect, 1)
                self.Received = []
                time.sleep(wait_time)
                while GPIO.input(Interrupt):
                        GPIO.output(ChipSelect, 0)
                        x = spi.readbytes(1)
                        print (x)
                        GPIO.output(ChipSelect, 1)
                        self.Received.append(x[0])
                        time.sleep(0.00002)         # Sleep functionality used
                        
                if len(self.Received)==4:
                        #print (self.Received)
                        self.Float = bytestofloat(self.Received)

                elif len(self.Received)==1:
                        print ("1 byte received")
                        self.Character = chr(self.Received[0])

                elif len(self.Received) > 5:
                        #print "String received"
                        self.String = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])

                elif len(self.Received)==5:
                        #print "5 byte received"
                        self.Version = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])

                

                        
                        
