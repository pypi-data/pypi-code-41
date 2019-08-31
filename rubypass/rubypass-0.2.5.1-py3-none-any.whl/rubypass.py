from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import logging
import logging.config

print ('(;^ω^)')

__version__ = '0.2.5.1'

fh = logging.FileHandler(filename='webBypass.log', mode='a')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh.setFormatter(formatter)

log = logging.getLogger('rubypass')
log.addHandler(fh)
log.setLevel(logging.INFO)

def klk(elem, driver):
	action = webdriver.common.action_chains.ActionChains(driver)

	driver.execute_script("arguments[0].scrollIntoView();", elem)
	action.move_to_element(elem).click().perform()

	log.debug('element clicked')

def getVod(driver):
	log.debug('video source extracted, v1')
	return driver.find_elements_by_xpath('//video')[0].get_attribute('src')

def getVod2(driver):
	a = driver.find_element_by_xpath('//iframe[@scrolling="no"]')

	driver.switch_to_frame(a)

	lol = driver.find_elements_by_xpath('//pjsdiv/video')[0].get_attribute('src')

	driver.switch_to.default_content()

	log.debug('video source extracted, v2')
	return lol

def firefoxDriverInit():
	firefox_profile = webdriver.FirefoxProfile()
	#firefox_profile.set_preference('permissions.default.stylesheet', 2)
	firefox_profile.set_preference('permissions.default.image', 2)
	firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
	firefox_profile.set_preference('dom.disable_beforeunload', True)
	firefox_profile.set_preference("media.volume_scale", "0.0")

	log.info('firefoxDriver loaded')

	return webdriver.Firefox(firefox_profile=firefox_profile)

def firefoxDriverInit2():
	firefox_profile = webdriver.FirefoxProfile()
	firefox_profile.set_preference('permissions.default.stylesheet', 2)
	firefox_profile.set_preference('permissions.default.image', 2)
	firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
	firefox_profile.set_preference('dom.disable_beforeunload', True)
	firefox_profile.set_preference("media.volume_scale", "0.0")

	log.info('firefoxDriver2 loaded')

	return webdriver.Firefox(firefox_profile=firefox_profile)

def seasonvarByPass(url, maxEps=30, delayz=(2, 0.6)):
	log.info('seasonvar season bypass init\n')
	log.info('url={}, maxEps={}'.format(url, maxEps))
	log.debug('delays used(in seconds) {}'.format(delayz))

	browser = firefoxDriverInit()

	browser.set_window_position(0, 0)
	browser.set_window_size(500, 500)

	try:
		browser.get(url)
		WebDriverWait(browser, 120).until(EC.presence_of_element_located((By.XPATH, '//span[@class="pgs-head"]')))

		log.debug('target loaded')

		#print (browser.current_url)

		time.sleep(delayz[0])

		vods = []
		ep = len(browser.find_elements_by_xpath('//pjsdiv[@style="position: relative; right: 0px; top: 0px; cursor: pointer; height: 50px; overflow: hidden; width: 170px; display: inline-block; line-height: 1.5em; vertical-align: top; white-space: normal;"]'))

		log.debug(ep)

		if ep > maxEps:
			ep = maxEps

			#print ('maxed out, capping to {}'.format(ep))

		ETA = ep*3

		#print ('ETA {}s'.format(ETA))
		log.info('ETA {}s'.format(ETA))
		#print (ep)


		subElem = browser.find_elements_by_xpath('//li[@data-translate="1"]')

		if len(subElem) != 0:
			log.debug('original dub obj found')

			klk(subElem[0], browser)
			log.debug('original dub obj clicked')

		log.debug('{} episodes to extract'.format(ep))
		log.debug('starting episode extract')

		for i in range(ep):
			try:
				elem = browser.find_element_by_xpath('//pjsdiv[@fid="{}" and @style="position: relative; right: 0px; top: 0px; cursor: pointer; height: 50px; overflow: hidden; width: 170px; display: inline-block; line-height: 1.5em; vertical-align: top; white-space: normal;"]'.format(i))
				klk(elem, browser)

				adElem = browser.find_element_by_xpath('//pjsdiv[@id="oframehtmlPlayer"]')

				time.sleep(delayz[1])

				klk(adElem, browser)

				aw = browser.window_handles
				if len(aw) >= 2:
					browser.switch_to_window(aw[1])
					browser.close()
					browser.switch_to_window(aw[0])

				vods.append(getVod(browser))

			except Exception as e:
				log.debug('episode {} failed: {}'.format(i, e))
				vods.append('failed')

		browser.quit()
		log.debug('done')

	except Exception as e:
		browser.quit()

		log.error('seasonvar season bypass failed', exc_info=True)

		return True, None, None

	log.info('seasonvar season bypass complete')

	return False, vods, ep

def seasonvarByPassEp(url, ep, delayz=(2, 3, 2)):
	log.info('seasonvar episode bypass init\n')
	log.info('url={}, ep={}'.format(url, ep))
	log.debug('delays used(in seconds) {}'.format(delayz))
	ep2 = ep

	browser = firefoxDriverInit()

	browser.set_window_position(0, 0)
	browser.set_window_size(500, 500)

	try:
		browser.get(url)
		WebDriverWait(browser, 120).until(EC.presence_of_element_located((By.XPATH, '//span[@class="pgs-head"]')))

		log.debug('target loaded')

		time.sleep(delayz[0])

		#print (browser.current_url)

		try:
			epLen = len(browser.find_elements_by_xpath('//pjsdiv[@style="position: relative; right: 0px; top: 0px; cursor: pointer; height: 50px; overflow: hidden; width: 170px; display: inline-block; line-height: 1.5em; vertical-align: top; white-space: normal;"]'))


			log.debug(epLen)

			if 1 <= ep <= epLen:
				pass

			else:
				if 1 > ep:
					ep = 1
					#print ('mined out, capping to {}'.format(ep))

				elif epLen < ep:
					ep = epLen
					#print ('maxed out, capping to {}'.format(ep))

		except Exception as e:
			log.debug('failed to get episode count of the show: {}'.format(e))
			ep = ep2

		#print (ep)


		subElem = browser.find_elements_by_xpath('//li[@data-translate="1"]')

		if len(subElem) != 0:
			log.debug('original dub obj found')

			klk(subElem[0], browser)
			log.debug('original dub obj clicked')

		time.sleep(delayz[1])

		elem = browser.find_element_by_xpath('//pjsdiv[@fid="{}" and @style="position: relative; right: 0px; top: 0px; cursor: pointer; height: 50px; overflow: hidden; width: 170px; display: inline-block; line-height: 1.5em; vertical-align: top; white-space: normal;"]'.format(ep-1))

		log.debug('target episode obj found')

		klk(elem, browser)
		klk(elem, browser)
		log.debug('target episode obj clicked')

		time.sleep(delayz[2])

		vod = getVod(browser)

		browser.quit()
		log.debug('done')

	except Exception as e:
		browser.quit()

		log.error('seasonvar episode bypass failed', exc_info=True)

		return True, None, None

	log.info('seasonvar episode bypass complete')

	return False, vod, ep

def showInfo(url, delayz=(2,)):
	log.info('seasonvar info bypass init\n')
	log.info(url)
	log.debug('delays used(in seconds) {}'.format(delayz))

	browser = firefoxDriverInit()

	browser.set_window_position(0, 0)
	browser.set_window_size(500, 500)

	try:
		browser.get(url)

		WebDriverWait(browser, 120).until(EC.presence_of_element_located((By.XPATH, '//div[@class="content-wrap"]')))

		log.debug('target loaded')

		time.sleep(delayz[0])

		#print (browser.current_url)

		log.debug('getting information')
		ep = len(browser.find_elements_by_xpath('//pjsdiv[@style="position: relative; right: 0px; top: 0px; cursor: pointer; height: 50px; overflow: hidden; width: 170px; display: inline-block; line-height: 1.5em; vertical-align: top; white-space: normal;"]'))

		#print (ep)

		lolz = []

		seasonsObj = browser.find_elements_by_xpath('//h2/a')


		for i in seasonsObj:
			if i != url:
				lolz.append('<{}>'.format(i.get_attribute('href')))

			else:
				lolz.append('{} <<< current url'.format(i.get_attribute('href')))

		browser.quit()
		log.debug('done')

	except Exception as e:
		browser.quit()

		log.error('seasonvar info bypass failed', exc_info=True)

		return True, None, None

	log.info('seasonvar info bypass complete')

	return False, lolz, ep

def animevostBypassEp(url, ep, delayz=(2, 1)):
	log.info('animevost episode bypass init\n')
	log.info('url={}, ep={}'.format(url, ep))
	log.debug('delays used(in seconds) {}'.format(delayz))
	ep2 = ep

	browser = firefoxDriverInit()

	browser.set_window_position(0, 0)
	browser.set_window_size(500, 500)

	try:
		browser.get(url)

		WebDriverWait(browser, 120).until(EC.presence_of_element_located((By.XPATH, '//div[@class="functionPanel"]')))

		log.debug('target loaded')

		time.sleep(delayz[0])

		try:
			name = browser.find_element_by_xpath('//div[@class="shortstoryHead"]/h1').text

			log.debug(name)

			name = name.replace('\n', ' ').rsplit(']')[0].rsplit('[')[1].split(' ')[0].split('-')

			if int(name[0]) <= ep <= int(name[1]):
				pass

			else:
				if int(name[0]) > ep:
					ep = int(name[0])
					#print ('mined out, capping to {}'.format(ep))

				elif int(name[1]) < ep:
					ep = int(name[1])
					#print ('maxed out, capping to {}'.format(ep))
		except Exception as e:
			log.debug('failed to get episode count of the show: {}'.format(e))
			ep = ep2

		epElem = browser.find_element_by_xpath('//div[@id="p{}"]'.format(ep-1))

		log.debug('target episode obj found')

		klk(epElem, browser)
		log.debug('target episode obj clicked')
		time.sleep(delayz[1])

		vod2 = getVod2(browser)

		browser.quit()
		log.debug('done')

	except Exception as e:
		browser.quit()

		log.error('animevost episode bypass failed', exc_info=True)

		return True, None, None

	log.info('animevost episode bypass complete')

	return False, vod2, ep

def animevostInfo(url, delayz=(2,)):
	log.info('animevost info bypass init\n')
	log.info(url)
	log.debug('delays used(in seconds) {}'.format(delayz))
	browser = firefoxDriverInit2()

	browser.set_window_position(0, 0)
	browser.set_window_size(500, 500)

	try:
		browser.get(url)

		WebDriverWait(browser, 120).until(EC.presence_of_element_located((By.XPATH, '//div[@class="functionPanel"]')))

		log.debug('target loaded')

		time.sleep(delayz[0])

		log.debug('getting information')

		name = browser.find_element_by_xpath('//div[@class="shortstoryHead"]/h1').text

		log.debug(name)

		eps = [int(i) for i in name.rsplit(']')[0].rsplit('[')[1].split(' ')[0].split('-')]
		name = name.split('/')[1].split('[')[0].strip(' ')

		lolz = []
		for i in browser.find_elements_by_xpath('//div[@class="text_spoiler"]/ol/li/a'):
			r = '^{}'.format(re.escape(url.split('-')[0]))
			l = str(i.get_attribute('href'))

			if re.search(r, l) != None:
				lolz.append('{} <<< current url'.format(l))

			else:
				lolz.append('<{}>'.format(l))

		browser.quit()
		log.debug('done')

	except Exception as e:
		browser.quit()

		log.error('animevost info bypass failed', exc_info=True)

		return True, None, None

	log.info('animevost info bypass complete')

	return False, eps, name, lolz


def animevostBypass(url, epRange=None, maxEps=40, delayz=(2, 0.8)):
	log.info('animevost season bypass init\n')
	log.info('url={}, maxEps={}'.format(url, maxEps))
	log.debug('delays used(in seconds) {}'.format(delayz))

	browser = firefoxDriverInit()

	browser.set_window_position(0, 0)
	browser.set_window_size(500, 500)

	try:
		browser.get(url)

		WebDriverWait(browser, 120).until(EC.presence_of_element_located((By.XPATH, '//div[@class="functionPanel"]')))

		log.debug('target loaded')

		time.sleep(delayz[0])

		try:
			name = browser.find_element_by_xpath('//div[@class="shortstoryHead"]/h1').text

			log.debug(name)

			name = [int(i) for i in name.split(']')[0].split('[')[1].split(' ')[0].split('-')]

			if epRange != None:
				if epRange[1] > int(name[1]):
					epRange[1] = int(name[1])

				if epRange[0] < 0:
					epRange[0] = 0

				if epRange[1]-epRange[0] > maxEps:
					epRange = None

			if epRange != None:
				name[0] = epRange[0]
				name[1] = epRange[1]

			if int(name[1]) > maxEps:
				name[1] = maxEps

			if int(name[0]) > 0:
				name[0] -= 1

			ETA = name[1]*1.25

		except Exception as e:
			log.debug('failed to get episode count of the show: {}'.format(e))
			name = (0, 1)
			ETA = -1

		#print ('ETA {}s'.format(ETA))
		log.info('ETA {}s'.format(ETA))

		lolz = []

		log.debug('{} episodes to extract'.format(name[1]))
		log.debug('starting episode extract')

		for i in range(name[0], name[1]):
			try:
				epElem = browser.find_element_by_xpath('//div[@id="p{}"]'.format(i))

				klk(epElem, browser)
				time.sleep(delayz[1])

				lolz.append(getVod2(browser))

			except Exception as e:
				log.debug('episode {} failed: {}'.format(i, e))
				lolz.append('failed')

		browser.quit()
		log.debug('done')

	except Exception as e:
		browser.quit()

		log.error('animevost season bypass failed', exc_info=True)

		return True, None, None

	log.info('animevost season bypass complete')

	return False, lolz, name[1]

def ppp(li, episode=None):
	obj = enumerate(li)

	if episode != None:
		obj = zip(range(episode-len(li), episode), li)

	for i2, i in obj:
		print ('{} => {}'.format(i2+1, i))