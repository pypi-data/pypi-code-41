# coding: utf8
__doc__ = 'bitmaps predefined'
__author__ = 'Peng Shulin <trees_peng@163.com>'
__license__ = 'MCUSH designed by Peng Shulin, all rights reserved.'

class Bitmap():
    def __init__( self, bitmap_str ):
        self.bitmap = bitmap_str
        self.height = len(bitmap_str)
        self.width = len(bitmap_str[0])
        
    def getPixel( self, x, y ):
        return not bool(self.bitmap[y][x] in ' _-0')


EMPTY = Bitmap([
    '--------',
    '--------',
    '--------',
    '--------',
    '--------',
    '--------',
    '--------',
    '--------', ])


HEART = Bitmap([
    '-**--**-',
    '*--**--*',
    '*------*',
    '*------*',
    '-*----*-',
    '-*----*-',
    '--*--*--',
    '---**---', ])

HEART2 = Bitmap([
    '-**--**-',
    '********',
    '********',
    '********',
    '-******-',
    '-******-',
    '--****--',
    '---**---', ])

#EATER_R = Bitmap([
#    '--****--',
#    '-*----*-',
#    '*---*-**',
#    '*----*--',
#    '*---*---',
#    '*---****',
#    '-*----*-',
#    '--****--', ])
#
#EATER_RC = Bitmap([
#    '--****--',
#    '-*----*-',
#    '*---*--*',
#    '*------*',
#    '*------*',
#    '*---****',
#    '-*----*-',
#    '--****--', ])
#
#EATER_L = Bitmap([
#    '--****--',
#    '-*----*-',
#    '**-----*',
#    '--**---*',
#    '--**---*',
#    '**-----*',
#    '-*----*-',
#    '--****--', ])


FAN1 = Bitmap([
    '----*---',
    '----*---',
    '----*---',
    '*****---',
    '---*****',
    '---*----',
    '---*----',
    '---*----', ])

FAN2 = Bitmap([
    '--------',
    '-*----*-',
    '--*--*--',
    '---**---',
    '---**---',
    '--*--*--',
    '-*----*-',
    '--------', ])

ARROW_TOP_LEFT = Bitmap([
    '******--',
    '*****---',
    '*****---',
    '******--',
    '*******-',
    '*--*****',
    '----***-',
    '-----*--', ])

ARROW_TOP_RIGHT = Bitmap([
    '--******',
    '---*****',
    '---*****',
    '--******',
    '-*******',
    '*****--*',
    '-***----',
    '--*-----', ])

ARROW_BOTTOM_LEFT = Bitmap([
    '-----*--',
    '----***-',
    '*--*****',
    '*******-',
    '******--',
    '*****---',
    '*****---',
    '******--', ])

ARROW_BOTTOM_RIGHT = Bitmap([
    '--*-----',
    '-***----',
    '*****--*',
    '-*******',
    '--******',
    '---*****',
    '---*****',
    '--******', ])



