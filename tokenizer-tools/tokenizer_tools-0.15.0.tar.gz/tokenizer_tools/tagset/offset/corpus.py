from tokenizer_tools.conllz.reader import read_conllx
from tokenizer_tools.conllz.writer import write_conllx
from tokenizer_tools.converter.conllz_to_offset import conllz_to_offset
from tokenizer_tools.converter.offset_to_sentence import offset_to_sentence


class Corpus(list):
    @classmethod
    def read_from_file(cls, data_file):
        with open(data_file, "rt") as fd:
            sentence_list = read_conllx(fd)

        offset_data_list = []
        for sentence in sentence_list:
            offset_data, result = conllz_to_offset(sentence)

            offset_data_list.append(offset_data)

        return Corpus(offset_data_list)

    def write_to_file(self, output_file):
        sentence_list = [offset_to_sentence(offset) for offset in self]

        with open(output_file, "wt") as fd:
            write_conllx(sentence_list, fd)
