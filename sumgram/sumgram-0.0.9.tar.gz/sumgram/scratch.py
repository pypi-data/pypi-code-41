import logging
from genericCommon import dumpJsonToFile
from sumgram import get_top_ngrams

ngram = 2
params = {
	'top_ngram_count': 20,
	'ngram_printing_mw': 60,
	'no_mvg_window_glue_split_ngrams': False,
	'title': '*TITLE*'
}

doc_List = [
	{'idu': 'x', 'text': 'The eye of Category 4 Hurricane Harvey is now over Aransas Bay. A station at Aransas Pass run by the Texas Coastal Observing Network recently reported a sustained wind of 102 mph with a gust to 132 mph. A station at Aransas Wildlife Refuge run by the Texas Coastal Observing Network recently reported a sustained wind of 75 mph with a gust to 99 mph. A station at Rockport reported a pressure of 945 mb on the western side of the eye.'},
	{'idu': 'y', 'text': 'Eye of Category 4 Hurricane Harvey is almost onshore. A station at Aransas Pass run by the Texas Coastal Observing Network recently reported a sustained wind of 102 mph with a gust to 120 mph.'},
	{'idu': 'z', 'text': 'Hurricane Harvey has become a Category 4 storm with maximum sustained winds of 130 mph. Sustained hurricane-force winds are spreading onto the middle Texas coast.'}
]

#logging.basicConfig(format='%(message)s', level=logging.INFO)
#logger = logging.getLogger(__name__)


#logger.info("starting script")

rep = get_top_ngrams(doc_List, ngram, params=params)

#print(rep.keys())
#logger.info("done with script")
#dumpJsonToFile('output.json', rep)