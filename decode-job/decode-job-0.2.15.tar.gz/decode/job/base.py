import os
import re
import json
import logging
import itertools
import requests
import hashlib

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.options import FirefoxProfile
from selenium.webdriver.chrome.options import Options as GoogleOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .storage.factory import get_storage_backend
from proxy_requests import ProxyRequests


class Job():
    env = 'pme'
    debug = True
    url_toth = 'https://toth.decode-pme.pactual.net/upload/'

    from selenium.webdriver.common.by import By
    """
    A class to inherit and run general jobs with ready to use tools such as
    selenium browsers, reverse proxy, storage and tests.

    To change the execution of the job just override the run method.

    Helper Methods:

    # self.get_browser(use_proxy=False/True)
      Return a headless Firefox browser that accepts 
      any certificate. Use proxy tries to use reverse proxy to hide IP

    # self.storage.delete(filepath, bucket_name=None)
      Deletes a file from bucket (if s3) or filesystem

    # self.storage.save(filename, content, bucket_name=None)
      Saves a file with the 'content' as string into bucket  (if s3) or filesystem

    # self.storage.read(filepath, bucket_name=None)
      Get the contents of a file from bucket (if s3) or filesystem

    """

    def download_file(self, url, filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return filename

    def convert_pdf_to_txt(self, path):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        for page in PDFPage.get_pages(
                fp,
                pagenos,
                maxpages=maxpages,
                password=password,
                caching=caching,
                check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        text = re.sub("\(cid:\d{0,3}\)", "", text)
        return text

    def __init__(self, storage_type="s3", logger=None):
        if not logger:
            self.logger = logging.getLogger("Job")
        else:
            self.logger = logger

        try:
            config = None
            with open('config.json', 'r') as f:
                config = json.loads(str(f.read()))
            f.close()
            self.env = config['env']
            self.debug = (str(config['debug'])=='true')
            self.url_toth = ''.join([ api[self.env] for api in config['toth'] if self.env in api ])
        except Exception as e:
            self.logger.error('config.json file not set')
            # exit(0)

        self.logger.info('env {} set'.format(self.env))

        if not os.getenv("DCD_CLIENT_SIGNATURE"):
            self.logger.error('env variable DCD_CLIENT_SIGNATURE not set')
            exit(0)
        self.storage = get_storage_backend(type=storage_type, logger=logger)

    def wait_for(self, firefox, by, key, delay=5):
        try:
            WebDriverWait(firefox, delay).until(
                EC.presence_of_element_located((by, key)))
            return True
        except TimeoutException:
            self.logger.error(
                f"WebDriverWait Timeout reached! Cannot find {key} for item")
            return False

    def bs4_element_to_selenium_web_element(self, browser, element):
        return browser.find_element_by_xpath(self.xpath_soup(element))

    def xpath_soup(self, element):
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            previous = itertools.islice(parent.children, 0,
                                        parent.contents.index(child))
            xpath_tag = child.name
            xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
            components.append(xpath_tag if xpath_index == 1 else '%s[%d]' %
                              (xpath_tag, xpath_index))
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)

    def clean_html(self, text):
        if not isinstance(text, str):
            text = text.text

        cleaned = text.replace("\n", " ").replace("\r", "").replace(
            "\t", "").replace("\xa0", "").replace("\\n", " ").replace(
                "\\r", "").replace("\\t", "")
        cleaned = re.sub("\s+", " ", cleaned)
        cleaned = re.sub('<.*?>', '', cleaned)
        cleaned = cleaned.replace("<", "").replace(">", "")
        return cleaned.strip()

    def configure_proxy(self, profile):
        MAX_ATTEMPS = 10
        while MAX_ATTEMPS > 0:
            req = ProxyRequests("https://www.google.com/")
            req.get()
            pr = req.get_proxy_used().split(":")
            if len(pr) > 1:
                pr[1] = int(pr[1])
                profile.set_preference("network.proxy.type", 1)
                profile.set_preference("network.proxy.http", pr[0])
                profile.set_preference("network.proxy.http_port", pr[1])
                profile.set_preference("network.proxy.ssl", pr[0])
                profile.set_preference("network.proxy.ssl_port", pr[1])
                self.logger.info(
                    "Successfuly configured proxy with http %s and port %s" %
                    (pr[0], pr[1]))
                return profile
            MAX_ATTEMPS -= 1
        self.logger.info(
            "Proxy configuration reached 10 attempts unsuccessfully. Skipping..."
            % (pr[0], pr[1]))
        return profile

    def get_remote_browser(self):
        raise NotImplementedError("Selenium grid is not running yet.")

    def get_browser(self, headless=True, use_proxy=False, bin_path=None, download_path=None, use_browser='Firefox'):
        if use_browser=='Firefox':
            options = FirefoxOptions()
            profile = FirefoxProfile()

            browser_download_dir = os.path.dirname(os.path.abspath(__file__))
            if download_path:
                browser_download_dir = download_path
            if self.debug:
                print(browser_download_dir)

            profile.set_preference("browser.download.dir", browser_download_dir);
            profile.set_preference("browser.download.folderList",2);
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf,application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream");
            profile.set_preference("browser.download.manager.showWhenStarting",False);
            profile.set_preference("browser.helperApps.neverAsk.openFile","application/pdf,application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream");
            profile.set_preference("browser.helperApps.alwaysAsk.force", False);
            profile.set_preference("browser.download.manager.useWindow", False);
            profile.set_preference("browser.download.manager.focusWhenStarting", False);
            profile.set_preference("browser.download.manager.alertOnEXEOpen", False);
            profile.set_preference("browser.download.manager.showAlertOnComplete", False);
            profile.set_preference("browser.download.manager.closeWhenDone", True);
            profile.set_preference("pdfjs.disabled", True);
            profile.set_preference("plugin.scan.Acrobat", "99.0");
            profile.set_preference("plugin.scan.plid.all", False);

            profile.accept_untrusted_certs = True

            if headless:
                options.add_argument('--headless')
            if use_proxy:
                profile = self.configure_proxy(profile)
            
            try:
                if bin_path: 
                    path_to_bin = bin_path 
                else:
                    if os.path.isfile('geckodriver.exe'): 
                        path_to_bin = 'geckodriver.exe'
                    else:
                        if os.getenv("DCD_DRIVE_PATH_BIN"):
                            path_to_bin = os.getenv("DCD_DRIVE_PATH_BIN")+'/geckodriver.exe'
                        else: 
                            raise Exception('env variable DCD_DRIVE_PATH_BIN not set.')

                browser = webdriver.Firefox(executable_path=path_to_bin, options=options, firefox_profile=profile)
            except Exception as e:
                exit(0)

            if use_proxy:
                # Precisamos testar o Proxy, então tentamos visitar a página do blank.org
                browser.get("https://blank.org/")

        else:
            options = GoogleOptions()

            if headless:
                options.add_argument('--headless')
            else:
                options.add_argument("--start-maximized")
            if use_proxy:
                MAX_ATTEMPS = 10
                while MAX_ATTEMPS > 0:
                    req = ProxyRequests("https://www.google.com/")
                    req.get()
                    pr = req.get_proxy_used().split(":")
                    if len(pr) > 1:
                        pr[1] = int(pr[1])
                        self.logger.info(
                            "Successfuly configured proxy with http %s and port %s" %
                            (pr[0], pr[1]))
                        break
                    MAX_ATTEMPS -= 1
                self.logger.info("Proxy configuration reached 10 attempts unsuccessfully. Skipping...")

                if MAX_ATTEMPS > 0:
                    options.add_argument('--proxy-server=%s:%s' % (pr[0], pr[1]))
            
            try:
                if bin_path: 
                    path_to_bin = bin_path 
                else:
                    if os.path.isfile('chromedriver.exe'): 
                        path_to_bin = 'chromedriver.exe'
                    else:
                        if os.getenv("DCD_DRIVE_PATH_BIN"):
                            path_to_bin = os.getenv("DCD_DRIVE_PATH_BIN")+'/chromedriver.exe'
                        else: 
                            raise Exception('env variable DCD_DRIVE_PATH_BIN not set.')

                browser = webdriver.Chrome(executable_path=path_to_bin, options=options)
            except Exception as e:
                exit(0)

        self.logger.info(
            "Created browser with executor URL %s and session_id %s" %
            (browser.command_executor._url, browser.session_id))
        return browser

    def upload_file(self, file_name, mime_type, source, source_table, category, owner, bucket_name, client_signature):
        try:
            ret = ''
            file_md5 = hashlib.md5((file_name+client_signature).encode('utf-8')).hexdigest()
            f = open(file_name, 'rb')
            files =  { 'files': (file_name, f) }

            header = {
                'dcd-client-signature': client_signature,
                'dcd-data-mime-type': mime_type,
                'dcd-data-md5': file_md5,
                'dcd-data-category': category,
                'dcd-filename': file_name,
                'dcd-data-src': source,
                'dcd-data-src-table': source_table,
                'dcd-data-owner': owner,
                'dcd-bucket-name': bucket_name,
                'Connection': 'keep-alive'
            }

            r = requests.post(self.url_toth, files=files, headers=header, verify=False)
            self.logger.info(r.status_code)
            self.logger.info(r.text)
            # import ipdb
            # ipdb.set_trace()
            return True 
        except TimeoutException:
            self.logger.error(
                f"WebDriverWait Timeout reached! Cannot find {key} for item")
            return False

    def select_by_text(self, browser, element, text, scroll_to_element=True):
        try:
            text = str(text)
            select_box = WebDriverWait(browser, 10).until(EC.element_to_be_clickable(element))
            if scroll_to_element:
                browser.execute_script("return arguments[0].scrollIntoView();", select_box)
            for option in select_box.find_elements_by_tag_name("option"):
                self.logger.info(option.text)
                if option.text == text:
                    option.click() 
                    break
        except Exception as e:
            self.logger.error(
                f"WebDriverWait Error! {e}")
            return False

        self.logger.info(element[1]+" "+text+" ok")
        return select_box

    def run(self):
        raise NotImplementedError("You have to overwrite the run() method")
