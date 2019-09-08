import tf_idf as terms, extract
import kivy,pprint,os,re
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.factory import Factory
import pandas as pd
import config


kivy.require('1.9.1')

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class PdfReaderMainScreen(Widget):

    #instance variables
    textinputtext = StringProperty()
    dirtext = StringProperty()
    #Dont need to pass in FILENAME here consider refactoring method call
    files = extract.opendir(config.pathName)

    # Why is this returning nothing when it getting output

    tf_idf_Keywords = terms.PDF_keywords()

    loadfile = ObjectProperty(None)
    text_input = ObjectProperty(None)


    def __init__(self,currentPage=None,**kwargs):
        super(PdfReaderMainScreen, self).__init__(**kwargs)
        self.currentPage = 0
        self.max = len(PdfReaderMainScreen.tf_idf_Keywords)

        self.textinputtext = str(PdfReaderMainScreen.tf_idf_Keywords)

        self.dirtext = str(PdfReaderMainScreen.files)


    def dismiss_popup(self):
        self._popup.dismiss()


    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                             size_hint=( 0.5,None), size=(400, 400))
        self._popup.open()


    def load(self,path, filename):
        # filename = path
        #with open(os.path.join(path, filename[0])) as stream:
            #self.text_input.text = stream.read()

        # result = str(os.path.join(path, filename))

        terms.run_tfidf(filename[0])
        opendir(filename[0])

        print("FilePath " + str(filename[0]))
        self.dismiss_popup()

        #Really dont need to return anything here !
        return filename[0]


    def generate_KeyWord_Btn(self):

        str_holder = ""
        # pd.set_option('display.max_columns', 100)
        # pd.set_option('display.max_rows', 500)
        # pd.set_option('display.max_columns', 500)
        # df = pd.DataFrame(PdfReaderMainScreen.tf_idf_Keywords[0],columns=['Term','  TDIDF'])

        for a_tuple in PdfReaderMainScreen.tf_idf_Keywords[0]:  # iterates through each tuple
            str_holder+='{}, '.format(*a_tuple)

        self.textinputtext  = str(str_holder)

        self.dirtext = str(PdfReaderMainScreen.files[0])
        #self.textinputtext  = ' term : {}'.format(str(terms.PDF_keywords()[0]))

    def generate_doclist(self):

        self.dirtext =  str(PdfReaderMainScreen.files[self.currentPage])


    def next_Btn(self):
        #Utlize instance variable to save the state
        if(self.currentPage <= self.max):
            try:
                print("Current Page %s" % (self.currentPage))

                #increment the counter
                self.currentPage +=1
                # pd.set_option('display.max_columns', 100)
                # pd.set_option('display.max_rows', 500)
                # pd.set_option('display.max_columns', 500)

                #df = pd.DataFrame(PdfReaderMainScreen.tf_idf_Keywords[self.currentPage],columns=['Term','TDIDF'])
                str_holder = ""
                for a_tuple in PdfReaderMainScreen.tf_idf_Keywords[self.currentPage]:  # iterates through each tuple
                        #Unpack tuple and format with comma
                        str_holder+='{}, '.format(*a_tuple)
                        #Unpack tuple and format with fix spaces
                        #str_holder+='{:<20} {}\n'.format(*a_tuple)

                #Display the keywords in GUI/make it viewable
                self.textinputtext = str(str_holder)
                self.dirtext =  str(PdfReaderMainScreen.files[self.currentPage])

            except KeyError:
                self.textinputteIxt = ""
                self.currentPage = self.max
                print("Set to last Page %s" % (self.max))
                return self.currentPage
        else:
            print("Page %s" % (self.currentPage))
            return True


    def previous_Btn(self):
        if(self.currentPage > 0):
            print("Current Page %s" % (self.currentPage))
            try:
                #decrement the counter
                str_holder = ""
                #increment the counter
                self.currentPage -=1
                # pd.set_option('display.max_columns', 100)
                # pd.set_option('display.max_rows', 500)
                # pd.set_option('display.max_columns', 500)
                # df = pd.DataFrame(PdfReaderMainScreen.tf_idf_Keywords[self.currentPage],columns=['Term','TDIDF'])
                for a_tuple in PdfReaderMainScreen.tf_idf_Keywords[self.currentPage]:  # iterates through each tuple
                        #Unpack tuple and format with fix spaces
                        str_holder+='{}, '.format(*a_tuple)

                #Display the keywords in GUI/make it viewable
                self.textinputtext = str(str_holder)
                self.dirtext =  str(PdfReaderMainScreen.files[self.currentPage])
            except KeyError:
                if self.currentPage == self.max:
                    self.currentPage = self.max
                    print('decrement the counter"')
            print("Previous Page %s" % (self.currentPage))

    def run_model():

        self.generate_KeyWord_Btn.disabled=True
        self.previous_Btn.disabled=True
        self.next_Btn = True
        t=Thread(target=run, args=())
        t.start()

        Clock.schedule_interval(partial(disable, t), 8)

    def disable(t, what):
        if not t.isAlive():
            self.load.disabled=False
            self.generate_KeyWord_Btn.disabled=False
            self.previous_Btn.disabled=False
            self.next_Btn= False
            return False

class PdfReaderUI(Widget):
    pass

class PdfReaderApp(App):
    def build(self):

        return  PdfReaderUI()

Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':
    PdfReaderApp().run()
