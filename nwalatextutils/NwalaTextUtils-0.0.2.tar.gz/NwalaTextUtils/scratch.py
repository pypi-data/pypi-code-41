import json
import logging

'''
from NwalaTextUtils.textutils import parallelGetTxtFrmURIs
from NwalaTextUtils.textutils import parallelGetTxtFrmFiles
from NwalaTextUtils.textutils import derefURI
from NwalaTextUtils.textutils import cleanHtml
from NwalaTextUtils.textutils import getPgTitleFrmHTML
'''
from textutils import parallelGetTxtFrmURIs
from textutils import parallelGetTxtFrmFiles
from textutils import derefURI
from textutils import cleanHtml
from textutils import getPgTitleFrmHTML


uris_lst = [
	'http://www.euro.who.int/en/health-topics/emergencies/pages/news/news/2015/03/united-kingdom-is-declared-free-of-ebola-virus-disease',
	'https://time.com/3505982/ebola-new-cases-world-health-organization/',
	'https://www.scientificamerican.com/article/why-ebola-survivors-struggle-with-new-symptoms/',
	'https://en.wikipedia.org/wiki/Ebola_virus',
	'http://www.realclearscience.com/journal_club/2014/04/21/a_possible_cure_for_ebola_virus_infection_108610.html',
	'http://www.nbcnews.com/storyline/ebola-virus-outbreak/who-declares-nigeria-ebola-free-after-42-days-no-cases-n229536',
	'http://www.independent.co.uk/news/world/africa/ebola-virus-top-sierra-leone-doctor-shek-umar-dies-of-disease-9636406.html',
	'http://www.nbcnews.com/storyline/ebola-virus-outbreak/exclusive-first-ebola-vaccine-trial-starts-africa-n222266',
	'http://www.theglobeandmail.com/news/national/canadian-researchers-thwart-ebola-virus/article4258104/',
	'http://www.who.int/mediacentre/factsheets/fs103/en/',
	'http://www.cnn.com/2014/08/07/world/ebola-virus-q-and-a/index.html',
	'http://www.healthline.com/health/ebola-hemorrhagic-fever',
	'https://www.nytimes.com/interactive/2014/07/31/world/africa/ebola-virus-outbreak-qa.html',
	'http://www.vanityfair.com/news/2014/10/ebola-virus-epidemic-containment'
]
params = {
	'loggerDets':{		
		'xlevel': logging.INFO,
		'.format': '',
		'.file': ''
	}
}

uri = 'https://time.com/3505982/ebola-new-cases-world-health-organization/'

#html = derefURI(uri, 0)
#plaintext = cleanHtml(html)
#title = getPgTitleFrmHTML(html)

#print('title:\n', title.strip(), '\n')
#print('html prefix:\n', html[:100].strip(), '\n')
#print('plaintext prefix:\n', plaintext[:100].strip(), '\n')

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info("starting script")


doc_lst = parallelGetTxtFrmURIs(uris_lst, updateRate=2)

logger.info("done with script")



'''
html:
	cleanHtml
	dereferenceURI
	extractPageTitleFromHTML
	parallelGetTxtFrmURIs

parallel:
	parallelTask
'''