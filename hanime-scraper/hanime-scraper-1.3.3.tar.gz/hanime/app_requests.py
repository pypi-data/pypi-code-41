from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import os
import time
import requests
from multiprocessing.dummy import Pool as ThreadPool

class HanimeScraper:

    counter = 0
    fileLocationToSave = ''

    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--window-size=1024,768")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--proxy-server='direct://'")
        self.chrome_options.add_argument("--proxy-bypass-list=*")
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--ignore-certificate-errors')
      
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['acceptSslCerts'] = True 
        capabilities['acceptInsecureCerts'] = True
    
        self.chrome_options.add_argument('user-agent')
        self.driver = webdriver.Chrome(options=self.chrome_options, executable_path='chromedriver.exe', desired_capabilities=capabilities)
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument("--proxy-bypass-list=*")

        #chrome_driver = 'G:/Python Projects/hanime/chromedriver.exe'
        #driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver, desired_capabilities=capabilities)    
        #self.driver = webdriver.Chrome('chromedriver.exe')
        self.driver.get('https://hanime.tv/browse/images')    
        #time.sleep(5)
        self.driver.save_screenshot(HanimeScraper.fileLocationToSave + 'screenshot_test.png')

                  
    def download_url(self,url):
        split_1 = url.split('uploads/')[1]
        split_2 = split_1.split('/')[1]
        fullpath = os.path.join(HanimeScraper.fileLocationToSave, split_2)
        if(os.path.exists(fullpath)):
            print(split_2 + ' file already exists @directory "' + fullpath + '"')
        else:
            print('Downloading :' + url)
            with requests.get(url, stream=True) as r:
                with open(fullpath, 'wb') as f:
                    for chunk in r:        
                        f.write(chunk)
        HanimeScraper.counter = HanimeScraper.counter+1          
                  

    def getUrls(self):
        fetch_links = self.driver.find_elements_by_xpath("//img[contains(@class, 'cuc__content')]")
        link_list = [] # links

        for links in fetch_links:

            string_url = links.get_attribute("src").split('?')[0]
            link_list.append(string_url)
        return link_list

    def nextPage(self):
        get_pagination = self.driver.find_elements_by_xpath("//button[contains(@class, 'pagination__navigation')]")

        if(get_pagination):
            get_pagination[1].click()
            print('\nMoving to Next Page\n')
            time.sleep(1)
            return True
        else:
            print('\n\n\n\nMission Accomplished!\n\n\n')    
            return False
        

# main
if __name__ == '__main__':
    hanime_bot = HanimeScraper()
    looping = True
    print("Please set desired location for saving...")
    print('Example Format: C:/etc/YourFolder')
    print('HOW TO:')
    print('Create folder to anywhere you want')
    print('Copy paste filepath from properties or directory url')
    HanimeScraper.fileLocationToSave = input('Enter Directory: ')
    if '/' in HanimeScraper.fileLocationToSave:
        HanimeScraper.fileLocationToSave = HanimeScraper.fileLocationToSave + '/'
    elif '\\' in HanimeScraper.fileLocationToSave:
        HanimeScraper.fileLocationToSave = HanimeScraper.fileLocationToSave + '\\'


    if(os.path.exists(HanimeScraper.fileLocationToSave)):
        looping = True
        print(HanimeScraper.fileLocationToSave)
        print('File path exists! starting modules....')
    else:
        looping = False
        print('File path do not exists! try again!')


  

    while looping:
        start = time.time()
        pool = ThreadPool(10) 
        pool.map(hanime_bot.download_url, hanime_bot.getUrls())
        elapsedTime = time.time() - start
        print(str(elapsedTime) +'ms.')   
        looping = hanime_bot.nextPage()
        print('Downloading ' + str(hanime_bot.counter) + ' files....\n\n')
        

    hanime_bot.driver.quit()
    pass
    
        