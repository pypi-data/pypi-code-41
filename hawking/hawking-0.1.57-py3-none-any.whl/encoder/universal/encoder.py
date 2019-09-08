""" Google universal text encoder.

tf-hub-url: https://tfhub.dev/google/universal-sentence-encoder/2.
"""
import os
import time
import tensorflow as tf
import tensorflow_hub as hub
import tf_sentencepiece  # Not used directly but needed to import TF ops.


class UniversalTextEncoder:
    """ Google Universal Text Encoder. """
    def __init__(self,
            module_url='https://tfhub.dev/google/universal-sentence-encoder-large/3',
            module_cache_dir='/tmp/universal-encoder'):

        if not os.path.exists(module_cache_dir):
            os.system('mkdir -p {}'.format(module_cache_dir))
        st = time.time()
        os.environ['TFHUB_CACHE_DIR'] = module_cache_dir
        self.module_url = module_url
        print('Initializing tf....')
        g = tf.Graph()
        with g.as_default():
            self.text_input = tf.placeholder(dtype=tf.string, shape=[None])
            self.encoder = hub.Module(self.module_url)
            self.my_result = self.encoder(self.text_input)
            init_op = tf.group([tf.compat.v1.global_variables_initializer(), tf.compat.v1.tables_initializer()])
        g.finalize()    
        self.session = tf.compat.v1.Session(graph=g)
        self.session.run(init_op)

        print('Completed loading and initializing module: "%s". Elapsed time: "%.2f" s' % (self.module_url, time.time() - st))

    def batch_encode(self, phrases):
        """ Batch encode phrases into embedding vectors. """
        return self.session.run(self.my_result, feed_dict={self.text_input: phrases})

    def encode(self, phrase):
        """ Encode a single phrase into an embedding vector. """
        return self.batch_encode([phrase])


