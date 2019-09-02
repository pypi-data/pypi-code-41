from allennlp_datalawyer.models import CrfTaggerEnsemble
from allennlp_datalawyer.predictors import SentenceTaggerPredictor
from allennlp.common import Params
from allennlp.data import DatasetReader


# params = Params.from_file('ner_elmo_harem_ensemble.jsonnet')
# model = CrfTaggerEnsemble.from_params(vocab=None, params=params)
# dataset_reader = DatasetReader.from_params(params.pop('dataset_reader'))
# predictor = SentenceTaggerPredictor(model, dataset_reader)
# predictor.predict('Aos 18 dias do mês junho de 2015, nesta cidade de Limoeiro do Norte, às 08h29min, estando aberta a sessão da Única Vara do Trabalho de Limoeiro do Norte, na Sala de Audiências, situada na Rua Cândido Olímpio, n° 1655, Centro, sob a direção do Exmo(a). Juiz do Trabalho, Dr(a). MATEUS MIRANDA DE MORAES, foram por ordem do Sr(a). Juiz apregoados os litigantes: ANGELA MARIA DA SILVA SOARES, RECLAMANTE(S), E LIMA NORONHA COMERCIAL LTDA - ME, RECLAMADO(A).')
