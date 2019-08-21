"""
# Class AskForColor
Based on Tkinter, this class called "AskForColor" opens a window for the
user to set a color in RGB system. To get the value in format "#RRGGBB"
(used on Tkinter as a pattern), just use the "get( )" method.
A default color is needed. See the next example:

        from ask_for_color import AskForColor 
        ask = AskForColor("#1a2b3c")
        color = ask.get()


#############################################
###### THIS IS THE DOCUMENTATION OF THE CLASS

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
            ask = AskForColor('#123456',title='WINDOWname',ok='Get color',
                                                        cancel='Decline')            
            print(ask.get())            
            print(ask.getnum())
            
METHOD get() 
        This method returns the string color like "#123456"        
        If the dictionary key "reverse=True" is given, it returns the
        inverse color (negative).
        
        Example of use:        
            ask = AskForColor('#123456')            
            print(ask.get())            
            print(ask.get(reverse=False)) # this is the same as ask.get()
            print(ask.get(reverse=True))
        
        
        
        
METHOD getnum()        
        This method returns a tuple of int numbers like (18,52,86).        
        If the dictionary key "reverse=True" is given, it returns the
        inverse color (negative).
        
        Example of use:        
            ask = AskForColor('#123456')            
            print(ask.getnum())            
            print(ask.getnum(reverse=False)) # this is the same as ask.getnum()
            print(ask.getnum(reverse=True))
        
"""
# quando houver a importação, este arquivo __init__ será executado
from ask_for_color.ask_for_color import AskForColor

