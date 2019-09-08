""" Bert encoder (Online | Offline).

Online: bert text encoder using bert-as-a-service encoder. github: https://github.com/hanxiao/bert-as-service.
Offline: in process bert text encoder. github: https://github.com/huggingface/pytorch-transformers.
"""
import time
import numpy as np
import torch
from pytorch_transformers import BertModel, BertTokenizer
from bert_serving.client import BertClient
from hawking.encoder.universal import UniversalTextEncoder


class OnlineBertTextEncoder:
    def __init__(self, server_ip='127.0.0.1', port=5555):
        self.server_ip = server_ip
        self.client = BertClient(ip=self.server_ip, port=port)

    def async_encode(self, feeder, callback, context):
        for v in self.client.encode_async(feeder(), max_num_batch=context.size):
            callback(v, context)

    def batch_encode(self, phrases):
        """ Batch encode phrases into embedding vectors. """
        return self.client.encode(phrases)

    def encode(self, phrase):
        """ Encode single phrase into an embedding vector. """
        return self.batch_encode([phrase])


class BertTextEncoder:
    def __init__(self, pretrained_weights='bert-base-uncased'):
        model_class = BertModel
        tokenizer_class = BertTokenizer

        # Load pretrained model/tokenizer
        st = time.time()
        print('Loading BERT pre-trained model `{}`'.format(pretrained_weights))
        self.tokenizer = tokenizer_class.from_pretrained(pretrained_weights)
        self.model = model_class.from_pretrained(pretrained_weights)
        print('Loading BERT model completed. Elapsed time: %.2f secs' % (time.time() - st))

    def batch_encode(self, phrases):
        features = []
        for phrase in phrases:
            input_ids = torch.tensor([self.tokenizer.encode(phrase, add_special_tokens=True)])
            with torch.no_grad():
                # Models outputs are tuples
                # TODO(oleg): get second last layer
                last_hidden_states = self.model(input_ids)[0]
                features.append(np.average(last_hidden_states[0], axis=0))

        return features

    def encode(self, phrase):
        return self.batch_encode([phrase])[0]


def encode_phrase(phrase, server_ip='127.0.0.1', port=5555,
                  weights='universal-sentence-encoder-multilingual-qa/1'):
    """ single-line wrapper of XXXXBertTextEncoder. """
    if encode_phrase.enc is None:
        if weights.startswith('bert-base-'):
            encode_phrase.enc = BertTextEncoder(pretrained_weights=weights)
        elif weights == 'online-bert':
            encode_phrase.enc = OnlineBertTextEncoder(server_ip=server_ip, port=port)
        elif weights.startswith('universal-sentence-'):
            encode_phrase.enc = UniversalTextEncoder(module_url='https://tfhub.dev/google/' + weights)
        else:
            raise ValueError('Weight `{}` is not recognized.'.format(weights))
    return encode_phrase.enc.encode(phrase)


encode_phrase.enc = None
