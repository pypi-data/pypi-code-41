#!/usr/bin/env python
"""Build a character embedding model."""
import argparse
import os
from model import build_embedding_models, train_embedding_model
from callback import SimilarityCallback
from whatsapp import clean, load_chat_from_path
from text import Text
from data import TrainingData

# Default arguments for the generation of token embeddings.
EMBEDDING_DIMENSION = 64
CHARACTER_CONTEXT_WINDOW = 2
WORD_CONTEXT_WINDOW = 5
NUMBER_EVALUATION_NEIGHBOURS = 5
NUMBER_TRAINING_STEPS = 1000000

EVALUATION_CHARACTERS = ['a', 'A', 'R', 'x', '1']
EVALUATION_WORDS = ['andrew', 'run', 'hello', 'london', 'whatsapp']

TRAINING_DATA_PATH = 'training_data-{}-{}.pkl'


def generate_embeddings(
        raw_whatsapp_chat,
        embedding_dimension,
        number_training_steps,
        number_evaluation_neighbours,
        character_level=True,
        cache_training_data=False):
    """
    Generate embedding vectors at the word- or character-level from a history
    of Whatsapp messages.
    """
    if character_level:
        evaluation_tokens = EVALUATION_CHARACTERS
        window_size = CHARACTER_CONTEXT_WINDOW
    else:
        evaluation_tokens = EVALUATION_WORDS
        window_size = WORD_CONTEXT_WINDOW

    print('Loading and parsing text')
    whatsapp_chat = clean(raw_whatsapp_chat, character_level=character_level)
    print('Number of different token instances {}'.format(len(whatsapp_chat)))

    text = Text(whatsapp_chat)

    print(
        'Building embedding for vocabulary size {}'.format(text.vocabulary_size))

    model, evaluation_model = build_embedding_models(
        text.vocabulary_size, embedding_dimension)

    evaluation_examples = [text.token_to_index[c] for c in evaluation_tokens]

    similarity_callback = SimilarityCallback(
        number_evaluation_neighbours, evaluation_examples, text, evaluation_model)

    if not cache_training_data:
        training_data = TrainingData.from_text(text, window_size)

    else:
        data_type = 'char' if character_level else 'word'
        training_data_path = TRAINING_DATA_PATH.format(data_type, window_size)

        if os.path.exists(training_data_path):
            print('Loading training data from file')
            training_data = TrainingData.load(training_data_path)
        else:
            print('Generating training data from input text')
            training_data = TrainingData.from_text(text, window_size)
            print('Dumping training data to file')
            training_data.dump(training_data_path)

    print('Training the embedding')
    train_embedding_model(
        model, training_data, similarity_callback, number_training_steps)

    return model


if __name__ == '__main__':

    print('Running character embedding')

    parser = argparse.ArgumentParser()
    parser.add_argument('whatsap_chat_path', type=str)
    parser.add_argument('--embedding_dimension', type=int)
    parser.add_argument('--number_training_steps', type=int)
    parser.add_argument('--test_mode', type=bool)
    args = parser.parse_args()

    print('Loading chat from {}'.format(args.whatsap_chat_path))
    chat_data = load_chat_from_path(args.whatsap_chat_path)

    if args.test_mode:
        print('In test mode.')
        chat_data = chat_data[:100]

    print('Number of training steps: {}'.format(args.number_training_steps))
    print('Embedding dimensionality: {}'.format(args.embedding_dimension))

    print('Chat contains {} different messages'.format(len(chat_data)))
    generate_embeddings(
        chat_data,
        args.embedding_dimension or EMBEDDING_DIMENSION,
        args.number_training_steps or NUMBER_TRAINING_STEPS,
        NUMBER_EVALUATION_NEIGHBOURS,
        cache_training_data=True
    )
