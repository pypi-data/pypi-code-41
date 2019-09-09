from tokenizer_tools.tagset.converter.offset_to_biluo import offset_to_biluo
from tokenizer_tools.conllz.sentence import SentenceX


def offset_to_sentence(sequence):
    encoding = offset_to_biluo(sequence)  # may raise AssertionError

    sentence = SentenceX(word_lines=sequence.text, attribute_lines=[encoding], id=sequence.id)
    sentence.meta = {'label': sequence.label}
    sentence.meta.update(sequence.extra_attr)
    
    return sentence
