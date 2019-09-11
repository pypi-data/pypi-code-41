from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import time, sys

from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django_sso_app.core.apps.services.models import Service


class TestFunzionale(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    #def tearDownClass(cls):
    #    if cls.server_url == cls.live_server_url:
    #        super().tearDownClass()

    def setUp(self):
        #self.browser = webdriver.Chrome()
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("useAutomationExtension", False)
        self.browser = webdriver.Chrome(options=options)
        
        #self.browser = webdriver.FirefoxDriver()
        self.browser.implicitly_wait(1)
        
        self.service = Service.objects.create(name="example", url="https://www.example.com")
        
    def tearDown(self):
        self.browser.close()

    def identifica_titolo(self, titolo):
        # riconosce la pagina del partito dal titolo
        self.assertIn(titolo, self.browser.title)

    def tag_contiene_testo(self, tag, testo, in_testa=False):
        """
        in_testa ==> testo == lista[id_lista][0].text
        """
        elementi = self.browser.find_elements_by_tag_name(tag)
        self.assertTrue(len(elementi)>0, 'lista vuota')
        if in_testa:
            self.assertEqual(
                testo, elementi[0].text,
                'Elemento "{}" non in testa'.format(testo)
            )
        else:
            self.assertIn(
                testo, [el.text for el in elementi]
            )

    def compila_input_by_name(self, name_input, testo, enter=True, el='input'):
        input_x = self.browser.find_element_by_xpath('//'+el+'[@name="'+name_input+'"]')

        input_x.send_keys(testo)
        if enter:
          input_x.send_keys(Keys.ENTER)

        return input_x

    def compila_input_by_id(self, eid, testo, enter=True):
        input_x = self.browser.find_element_by_id(eid)
        input_x.send_keys(testo)
        if enter:
          input_x.send_keys(Keys.ENTER)
        return input_x

    def click_link(self, url):
        link = self.browser.find_element_by_xpath('//a[@href="'+url+'"]')
        print('\n LINKS elementi', link)
        link.click()
        
    def find_by_tag_class_and_text(self, tag, css, text):
        return self.browser.find_element_by_xpath("//{0}[contains(@class, '{1}') and text()='{2}']".format(tag, css, text))

    def find_by_tag_and_name(self, tag, name):
        return self.browser.find_element_by_xpath('//{0}[@name="{1}"]'.format(tag, name))

    def find_by_tag_and_class(self, tag, cls):
        return self.browser.find_element_by_xpath("//{0}[contains(@class, '{1}')]".format(tag, cls))
      
    def press_next_button(self, i):
        self.browser.find_elements_by_xpath('//{0}[@name="{1}"]'.format('button', 'next_step'))[i].click()

if __name__ == '__main__':
    try:
        unittest.main(warnings='ignore')

    except KeyboardInterrupt:
        print('Ricevura terminazione da tastiera')
        exit(0)
