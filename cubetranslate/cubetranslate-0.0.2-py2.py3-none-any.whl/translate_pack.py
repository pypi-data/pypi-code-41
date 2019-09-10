from acumos.modeling import Model, List
from acumos.session import AcumosSession
from acumos.metadata import Requirements
import translate_service

google_translate = translate_service.GoogleTranslate()

def translate( sentence: List[str]) -> str:
    return google_translate.translate( sentence)

model = Model(translate=translate)
session = AcumosSession()
reqs = Requirements(reqs=['googletrans'], scripts=['./translate_service.py'])
session.dump(model, '多语言翻译V1', './out/', reqs)