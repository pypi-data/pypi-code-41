from tkinter import Tk,Scale,Frame,Label,Button,HORIZONTAL

class AskForColor:
    __hasInstance = False
    def __init__(self,default_color,**kw):
        """
        This class AskForColor allows the user choose a color in RGB system.        

        obligatory input:
            > default_color = '#123456'
        
        inputs as a dictionary (optional):
            >  title = 'Window_title_example'
            >     ok = 'ok_button_text_example'
            > cancel = 'cancel_button_text_example'

        To get the color, use the method "get()";
        To get the integer numbers, use the method "getnum()".

        Example of use:
            ask = AskForColor('#123456',title='WINDOWname',ok='Get color',cancel='Decline')
            print(ask.get())
            print(ask.getnum())
        """
        
        kw.setdefault('title','Choose a color')
        kw.setdefault('ok','OK')
        kw.setdefault('cancel','Cancel')
        
        self.__cor_default = default_color
        self.__cor = default_color
        
        self.__numero = (self.__hexstr2int(self.__cor[1:3]),self.__hexstr2int(self.__cor[3:5]),self.__hexstr2int(self.__cor[5:7]))
        if not AskForColor.__hasInstance:
            AskForColor.__hasInstance = True
            self.__tk = Tk()
            self.__tk.title(kw['title'])
            self.__tk.resizable(False,False)
            
            self.__frame = Frame(self.__tk)
            self.__frame_botoes = Frame(self.__tk)
            self.__frame_labels = Frame(self.__tk)
            
            self.__frame.pack()
            self.__frame_labels.pack()
            self.__frame_botoes.pack()
            
            height = 20
            width = 500
            buttons_width = 10
            

            self.__slider_r = Scale(self.__frame, from_=0, to=255, orient=HORIZONTAL,width=height,length=width,fg='#ff0000')
            self.__slider_g = Scale(self.__frame, from_=0, to=255, orient=HORIZONTAL,width=height,length=width,fg='#00ff00')
            self.__slider_b = Scale(self.__frame, from_=0, to=255, orient=HORIZONTAL,width=height,length=width,fg='#0000ff')        

            self.__slider_r['command'] = self.__setcor
            self.__slider_g['command'] = self.__setcor
            self.__slider_b['command'] = self.__setcor

            self.__slider_r.set(self.__hexstr2int(self.__cor_default[1:3]))
            self.__slider_g.set(self.__hexstr2int(self.__cor_default[3:5]))
            self.__slider_b.set(self.__hexstr2int(self.__cor_default[5:7]))

            self.__slider_r['label'] = hex(self.__slider_r.get())[2:]
            self.__slider_g['label'] = hex(self.__slider_g.get())[2:]
            self.__slider_b['label'] = hex(self.__slider_b.get())[2:]
            
            self.__slider_r.pack()
            self.__slider_g.pack()
            self.__slider_b.pack()        
            

            self.__label = Label(self.__frame_labels,text=f'{self.__cor_default[1:].upper()}: ')
            self.__label.grid(row=0,column=0)        
            
            self.__label_cor = Label(self.__frame_labels,text=' '*15)
            self.__label_cor['bg'] = self.__cor
            self.__label_cor.grid(row=0,column=1)
            
            
            self.__ok = Button(self.__frame_botoes,text=kw['ok'],width=buttons_width)
            self.__ok['command'] = self.__retornook
            self.__ok.grid(row=0,column=0)
            
            
            self.__cancelar = Button(self.__frame_botoes,text=kw['cancel'],width=buttons_width)
            self.__cancelar['command'] = self.__retornocancel
            self.__cancelar.grid(row=0,column=1)        

            
            self.__tk.protocol('WM_DELETE_WINDOW', self.__retornocancel)
            self.__tk.mainloop()
            
        

    def __setcor(self,valor):        
        __cor  = '#' + self.__int2hexstr(self.__slider_r.get())
        __cor += self.__int2hexstr(self.__slider_g.get())
        __cor += self.__int2hexstr(self.__slider_b.get())
        self.__label_cor['bg'] = __cor
        self.__label['text'] = __cor[1:].upper()+': '
        self.__cor = __cor
        self.__numero = (self.__slider_r.get(),self.__slider_g.get(),self.__slider_b.get())
        self.__slider_r['label'] = "Hex: " + hex(self.__slider_r.get())[2:].upper() + "     % : {0:0.3f}".format(self.__slider_r.get()/255)
        self.__slider_g['label'] = "Hex: " + hex(self.__slider_g.get())[2:].upper() + "     % : {0:0.3f}".format(self.__slider_g.get()/255)
        self.__slider_b['label'] = "Hex: " + hex(self.__slider_b.get())[2:].upper() + "     % : {0:0.3f}".format(self.__slider_b.get()/255)

    def __retornook(self):
        self.__cor = self.__cor
        AskForColor.__hasInstance = False
        self.__tk.destroy()
        self.__tk.quit()
    
    def __retornocancel(self):
        self.__cor = self.__cor_default
        AskForColor.__hasInstance = False
        self.__tk.destroy()
        self.__tk.quit()

    def get(self,**kw):        
        """
        This method returns the string color like "#123456"
        If the dictionary key "reverse=True" is given, it returns the inverse color (negative).
        """
        kw.setdefault('reverse',False)
        if kw['reverse']:
            n1,n2,n3=self.getnum()
            n1,n2,n3=255-n1,255-n2,255-n3
            return '#'+self.__int2hexstr(n1)+self.__int2hexstr(n2)+self.__int2hexstr(n3)
        return self.__cor
                         
    def getnum(self,**kw):
        """
        This method returns a tuple of int numbers like (18,52,86).
        If the dictionary key "reverse=True" is given, it returns the inverse color (negative).
        """
        kw.setdefault('reverse',False)
        if kw['reverse']:
            return (255-self.__numero[0],255-self.__numero[1],255-self.__numero[2])
        return self.__numero
    

    def __hexstr2int(self,string):
        string = string.lower()
        n = len(string)
        dictt = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'a':10,'b':11,'c':12,'d':13,'e':14,'f':15}
        valor = 0
        exponent = 0
        for i in range(n-1,-1,-1):
            valor += dictt[string[i]] * (16**exponent)
            exponent +=1
        return valor

    def __int2hexstr(self,intt):
        if len(hex(intt)[2:])==2:
            return hex(intt)[2:]
        else:
            return '0'+hex(intt)[2:]

