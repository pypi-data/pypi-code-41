from typing import List
from overrides import overrides
from allennlp.data.tokenizers.token import Token
from allennlp.data.tokenizers.word_splitter import WordSplitter
from sacremoses import MosesTokenizer


@WordSplitter.register('moses')
class MosesWordSplitter(WordSplitter):

    def __init__(self):
        self.tokenizer = MosesTokenizer(lang='pt')

    """
    A ``WordSplitter`` that assumes you've already done your own tokenization somehow and have
    separated the tokens by spaces.  We just split the input string on whitespace and return the
    resulting list.  We use a somewhat odd name here to avoid coming too close to the more
    commonly used ``SpacyWordSplitter``.

    Note that we use ``sentence.split()``, which means that the amount of whitespace between the
    tokens does not matter.  This will never result in spaces being included as tokens.
    """
    @overrides
    def split_words(self, sentence: str) -> List[Token]:
        return [Token(t) for t in self.tokenizer.tokenize(sentence)]
