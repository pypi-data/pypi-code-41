#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import Image
import ImageFont
import ImageDraw
import ImageFilter
import gtk
import threading
from subprocess import Popen, PIPE, STDOUT
 
gtk.gdk.threads_init()
#--------------------------imagen construir--------------------------------
def gen_random_word(wordLen=6):
    allowedChars = "abcdefghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWZYZ0123456789"
    word = ""
    for i in range(0, wordLen):
        word = word + allowedChars[random.randint(0,0xffffff) % len(allowedChars)]
    return word
    
def gen_captcha(text, fnt, fnt_sz, file_name, fmt='JPEG'):      
    fgcolor = random.randint(0,1)
    bgcolor = fgcolor ^ 0xffffff
    font = ImageFont.truetype(fnt,fnt_sz)
    dim = font.getsize(text)
    im = Image.new('RGB', (dim[0]+5,dim[1]+5), bgcolor)
    d = ImageDraw.Draw(im)
    x, y = im.size
    r = random.randint
    for num in range(100):
        d.rectangle((r(0,x),r(0,y),r(0,x),r(0,y)),fill=r(0,0xffffff))
    d.text((3,3), text, font=font, fill=fgcolor)
    im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
    im.save(file_name, format=fmt)
#--------------------------------------------------------------------------
class PackBox1:
    
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("-* C A N A I M A *-")
        window.set_border_width(10)
        window.set_size_request(550, 200)
        window.set_resizable(False)
 
        
        def imagen_box2(homogeneous, spacing, expand, fill, padding):
    
            caja = gtk.HBox(homogeneous, spacing)
            caja.set_border_width(5)
    
            image = gtk.Image()
            image.set_from_file('test.jpg')
            caja.pack_start(image, gtk.TRUE, gtk.FALSE,0)
            image.show()
    
            return caja
        
        def make_box1(homogeneous, spacing, expand, fill, padding):
            
            def clic_boton(self):
                hilo = threading.Thread(target=validate, args=(self))
                hilo.start()
            
            def validate(self, data=None):
                                        
            
                if  texto.get_text() != word:
                
                    md=gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="El valor introducido no coincide con el captcha intente de nuevo")
                    md.run()
                    md.destroy()
                    
 
                else:   
                    md=gtk.MessageDialog(parent=None, flags=0, buttons=gtk.BUTTONS_OK, message_format="El valor introducido es Correcto")
                    md.run()
                    md.destroy()        
    
            caja = gtk.HBox(homogeneous, spacing)
            caja.set_border_width(10)
            
            etiqueta = gtk.Label("Introduzca el valor")
            #etiqueta.set_alignment(0,0)
            caja.pack_start(etiqueta, False, False, 30)
            etiqueta.show()
   
            texto = gtk.Entry(10)
            #texto.connect("activate", enter_callback)
            caja.pack_start(texto, False, False, 10)
            texto.show()
   
            boton = gtk.Button(stock=gtk.STOCK_OK)
            boton.connect("clicked", validate)
            caja.pack_start(boton, True, True, 40)
            boton.show()
            return caja
        
        def make_box3(homogeneous, spacing, expand, fill, padding):
   
            caja = gtk.HBox(homogeneous, spacing)
            caja.set_border_width(10)
            
            boton = gtk.Button(stock=gtk.STOCK_CLOSE)
            boton.connect("clicked", gtk.mainquit)
            caja.pack_start(boton, gtk.TRUE, gtk.TRUE, 70)
            boton.show()
            return caja
        
        box1 = gtk.VBox(False, 0)
        
        box2 = imagen_box2(False, 0, False, False,0)
        box1.pack_start(box2, False, False, 0)
        box2.show()
        
        box2 = make_box1(False, 0, False, False,0)
        box1.pack_start(box2, False, False, 0)
        box2.show()
        
        box2 = make_box3(False, 0, False, False,0)
        box1.pack_start(box2, False, False, 20)
        box2.show()
        
        box1.show()
        window.add(box1)
        window.show()
    
def main():
    gtk.main()
    return 0
            
if __name__ == '__main__':
    word = gen_random_word()
    gen_captcha(word.strip(), '/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf', 25, "test.jpg")
    packbox1 = PackBox1()
    main()