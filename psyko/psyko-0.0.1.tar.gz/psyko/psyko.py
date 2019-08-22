import pychrome

browser = None
tab = None
page = None


def open_browser():
    _start_chrome_process()
    browser = pychrome.Browser('http://127.0.0.1:9222')
    tab = browser.new_tab()
    tab.start()
    tab.Network.enable()


def goto(url: str):
    tab.Page.navigate(url=url)



def _start_chrome_process(host='127.0.0.1', port='9222'):
    pass
