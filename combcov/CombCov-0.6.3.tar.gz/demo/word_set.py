import itertools
import logging

from combcov import CombCov, Rule

logger = logging.getLogger("WordSet")


class WordSet(Rule):

    def __init__(self, alphabet=tuple(), avoid=frozenset(), prefix=""):
        self.alphabet = tuple(alphabet)
        self.avoid = self._basis_of(avoid)
        self.prefix = prefix
        self.max_prefix_size = max(0, max(len(av) for av in self.avoid))

    def contains(self, word):
        return all(av not in word for av in self.avoid)

    def next_lexicographical_word(self, from_word):
        if from_word is None:
            return ""

        else:
            word = list(from_word)

            # Increasing last character by one and carry over if needed
            for i in range(len(word)):
                pos = -(i + 1)
                char = word[pos]
                index = self.alphabet.index(char)
                next_index = index + 1
                if next_index == len(self.alphabet):
                    word[pos] = self.alphabet[0]
                    # ...and carry one over
                else:
                    word[pos] = self.alphabet[next_index]
                    return "".join(word)

            # If we get this far we need to increase the length of the word
            return self.alphabet[0] + "".join(word)

    @staticmethod
    def _basis_of(words):
        basis = set()
        words = list(reversed(sorted(words, key=len)))
        for i in range(len(words)):
            candidat = words[i]
            if all(word not in candidat for word in words[i + 1:]):
                basis.add(candidat)
        return frozenset(basis)

    @staticmethod
    def _get_all_subwords_of(s):
        # list of set because we don't want duplicates
        return sorted(list(
            set(s[i:j + 1] for i in range(len(s)) for j in range(i, len(s)))))

    def get_all_avoiding_subsets(self):
        avoiding_subwords = [self._get_all_subwords_of(avoid) for avoid in
                             self.avoid]
        return {frozenset(product) for product in
                itertools.product(*avoiding_subwords)}

    def get_elmnts(self, of_size):
        words_of_length = []

        padding = of_size - len(self.prefix)
        rest = self.alphabet[0] * padding

        while len(rest) == padding:
            if self.contains(rest):
                words_of_length.append(self.prefix + rest)
            rest = self.next_lexicographical_word(rest)

        return words_of_length

    def get_subrules(self):
        rules = 0
        prefixes = []
        for n in range(self.max_prefix_size):
            prefixes.extend(self.get_elmnts(n + 1))

        # Singleton rules, on the form prefix + empty WordSet
        for prefix in [''] + prefixes:
            empty_word_set = WordSet(alphabet=self.alphabet,
                                     avoid=frozenset(self.alphabet),
                                     prefix=prefix)
            rules += 1
            yield empty_word_set

        # Regular rules of the from prefix + non-empty WordSet
        for prefix in prefixes:
            for avoiding_subset in self.get_all_avoiding_subsets():
                subword_set = WordSet(self.alphabet, avoiding_subset, prefix)
                rules += 1
                yield subword_set

        logger.info("Generated {} subrules".format(rules))

    def _key(self):
        return (self.alphabet, self.avoid, self.prefix)

    def __repr__(self):
        return "'{}'*Av({})".format(self.prefix, ",".join(sorted(self.avoid)))

    def __str__(self):
        return "{} over ∑={{{}}}".format(repr(self),
                                         ",".join(sorted(self.alphabet)))


def main():
    logging.getLogger().setLevel(logging.INFO)

    alphabet = ('a', 'b')
    avoid = frozenset(['aa'])
    word_set = WordSet(alphabet, avoid)

    max_elmnt_size = 7
    comb_cov = CombCov(word_set, max_elmnt_size)
    comb_cov.print_outcome()


if __name__ == "__main__":
    main()
