import logging
import os
import time

from hawking.encoder.bert import OnlineBertTextEncoder, BertTextEncoder, encode_phrase
from hawking.encoder.inceptionresnetv2 import InceptionResNetV2ImageEncoder
from hawking.encoder.resnet50 import ResNet50ImageEncoder
from hawking.encoder.vgg import VGG16ImageEncoder, VGG19ImageEncoder
from hawking.encoder.universal import UniversalTextEncoder


def create_encoder(config={
                       "entity_type": "text",
                       "encoder_type": "universal-sentence-encoder",
                       "top_layer": "fc1000",
                       "print_summary": False,
                       "weights": "https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/1",
                       "encoder_host": "127.0.0.1",
                       "encoder_port": 5555,
                   }):
    """ Creating various encoder based on config.

    ResNet50 top-layer = 'fc1000'
    InceptionResNetV2 top-layer = 'predictions'
    """
    # TFHUB Caching 101: https://www.tensorflow.org/hub/basics.
    logging.info("Setting TFHUB_CACHE_DIR=/tmp.")
    os.environ["TFHUB_CACHE_DIR"] = "/tmp"
    st = time.time()
    logging.info(config)
    if config['entity_type'] == 'text':
        encoder_weights = config['weights']
        if config['encoder_type'] == 'online-bert':
            logging.info('Connecting to text encoder service `{}:{}`...'.format(config['encoder_host'],
                                                                                config['encoder_port']))
            encoder = OnlineBertTextEncoder(config['encoder_host'],
                                            config['encoder_port'])
        elif config['encoder_type'] == 'bert':
            encoder = BertTextEncoder(encoder_weights)
        elif config['encoder_type'] == 'universal-sentence-encoder':
            encoder = UniversalTextEncoder(encoder_weights)
        else:
            raise ValueError('encoder_weights `{}` is NOT supported.'.format(encoder_weights))
        logging.info('Successfully initialized text encoder with pre-trained weight `{}`.'.format(encoder_weights))
    elif config['entity_type'] == 'image':
        if config['encoder_type'] == 'resnet50':
            encoder = ResNet50ImageEncoder(top_layer=config['top_layer'], print_summary=config['print_summary'])
        elif config['encoder_type'] == 'inceptionresnetv2':
            encoder = InceptionResNetV2ImageEncoder(top_layer=config['top_layer'],
                                                    print_summary=config['print_summary'])
        elif config['encoder_type'] == 'vgg16':
            encoder = VGG16ImageEncoder(top_layer=config['top_layer'], print_summary=config['print_summary'])
        elif config['encoder_type'] == 'vgg19':
            encoder = VGG19ImageEncoder(top_layer=config['top_layer'], print_summary=config['print_summary'])
        else:
            raise ValueError('encoder_type:`{}` is not supported!'.format(config['encoder_type']))
    logging.info('Created encoder: %s. Elapsed time: %.2f' % (config['encoder_type'], time.time() - st))
    return encoder
