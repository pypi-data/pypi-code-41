"""Keras neural networks for different NLP tasks."""
import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.layers import Input, Dense, Reshape, Embedding, dot


def _reshape_embedding(input, embedding, name):
    return Reshape((embedding.output_dim, 1), name=name)(embedding(input))


def build_embedding_models(vocabulary_size, embedding_dimension):
    """
    Build neural network models to generate character embeddings.

    This function builds two models:
        1. Context classification model
        2. Cosine similarity model

    The context model is a discriminator. It takes in two elements as input: an
    input character and a testing character. The model outputs the probability
    that the testing character is found in the context of the input character.
    The model contains a single "embedding" layer, which is used to represent
    each character in some low-dimensional space. This embedding layer can later
    be extracted for use elsewhere.

    The similarity model is an evaluation model. It is used during training of
    the context model, to identify the cosine similarity of different character
    embeddings. Notionally, characters that are somehow similar should have a
    high cosine similarity.

    Parameters
    ----------
    vocabulary_size : int
        Number of unique characters within the vocabulary.
    embedding_dimension : int
        Dimension of the embedding vector. This should be lower than the
        vocabulary size.

    Returns
    -------
    context_model : tensorflow.keras.Model
    similarity_model : tensorflow.keras.Model
    """
    input_target = Input((1,), name='target_input')
    input_context = Input((1,), name='context_input')

    embedding = Embedding(vocabulary_size, embedding_dimension, input_length=1, name='embedding')

    target = _reshape_embedding(input_target, embedding, name='embedded_input')
    context = _reshape_embedding(input_context, embedding, name='embedded_context')

    dot_product = dot([target, context], axes=1, normalize=False, name='combine_input_context')
    dot_product = Reshape((1,), name='reshape_combination')(dot_product)

    output = Dense(1, activation='sigmoid', name='sigmoid_activation')(dot_product)

    context_model = Model(inputs=[input_target, input_context], outputs=output, name='skipgram_model')
    context_model.compile(loss='binary_crossentropy', optimizer='rmsprop')

    similarity = dot([target, context], axes=1, normalize=True)
    similarity_model = Model(inputs=[input_target, input_context], outputs=similarity)

    return context_model, similarity_model


def train_embedding_model(model, training_data, similarity_callback,
                          number_training_steps):
    """
    Train the context classification model.

    Parameters
    ----------
    model : tf.keras.Model
    training_data : waddle.text.Text
    similarity_callback : waddle.callback.SimilarityCallback
    number_training_steps : int
        Number of training steps to take in the gradient descent.
    """
    arr_1 = np.zeros((1,))
    arr_2 = np.zeros((1,))
    arr_3 = np.zeros((1,))

    for training_step in range(number_training_steps):
        training_example_index = np.random.randint(0, len(training_data.labels) - 1)

        arr_1[0] = training_data.target[training_example_index]
        arr_2[0] = training_data.context[training_example_index]
        arr_3[0] = training_data.labels[training_example_index]

        loss = model.train_on_batch([arr_1, arr_2], arr_3)

        if training_step % 1000 == 0:
            print("Iteration {}, loss={}".format(training_step, loss))

        if training_step % 10000 == 0:
            similarity_callback.run_sim()
