import itertools
import logging

from combcov import CombCov, Rule

logger = logging.getLogger("StringSet")


class StringSet(Rule):

    def __init__(self, alphabet=tuple(), avoid=frozenset(), prefix=""):
        self.alphabet = tuple(alphabet)
        self.avoid = frozenset(avoid)
        self.prefix = prefix
        self.max_prefix_size = max(0, max(len(av) for av in self.avoid))

    def contains(self, string):
        return all(av not in string for av in self.avoid)

    def next_lexicographical_string(self, from_string):
        if from_string is None:
            return ""

        else:
            string = list(from_string)

            # Increasing last character by one and carry over if needed
            for i in range(len(string)):
                pos = -(i + 1)
                char = string[pos]
                index = self.alphabet.index(char)
                next_index = index + 1
                if next_index == len(self.alphabet):
                    string[pos] = self.alphabet[0]
                    # ...and carry one over
                else:
                    string[pos] = self.alphabet[next_index]
                    return "".join(string)

            # If we get this far we need to increase the length of the string
            return self.alphabet[0] + "".join(string)

    @staticmethod
    def _get_all_substrings_of(s):
        # list of set because we don't want duplicates
        return sorted(list(
            set(s[i:j + 1] for i in range(len(s)) for j in range(i, len(s)))))

    def get_all_avoiding_subsets(self):
        avoiding_substrings = [self._get_all_substrings_of(avoid) for avoid in
                               self.avoid]
        return {frozenset(product) for product in
                itertools.product(*avoiding_substrings)}

    def get_elmnts(self, of_size):
        strings_of_length = []

        padding = of_size - len(self.prefix)
        rest = self.alphabet[0] * padding

        while len(rest) == padding:
            if self.contains(rest):
                strings_of_length.append(self.prefix + rest)
            rest = self.next_lexicographical_string(rest)

        return strings_of_length

    def get_subrules(self):
        rules = 0
        prefixes = []
        for n in range(self.max_prefix_size):
            prefixes.extend(self.get_elmnts(n + 1))

        # Singleton rules, on the form prefix + empty StringSet
        for prefix in [''] + prefixes:
            empty_string_set = StringSet(alphabet=self.alphabet,
                                         avoid=frozenset(self.alphabet),
                                         prefix=prefix)
            rules += 1
            yield empty_string_set

        # Regular rules of the from prefix + non-empty StringSet
        for prefix in prefixes:
            for avoiding_subset in self.get_all_avoiding_subsets():
                substring_set = StringSet(self.alphabet, avoiding_subset,
                                          prefix)
                rules += 1
                yield substring_set

        logger.info("Generated {} subrules".format(rules))

    def _key(self):
        return (self.alphabet, self.avoid, self.prefix)

    def __str__(self):
        return "'{}'*Av({}) over ∑={{{}}}".format(self.prefix,
                                                  ",".join(self.avoid),
                                                  ",".join(self.alphabet))


def main():
    logging.getLogger().setLevel(logging.INFO)

    alphabet = ('a', 'b')
    avoid = frozenset(['aa'])
    string_set = StringSet(alphabet, avoid)

    max_elmnt_size = 7
    comb_cov = CombCov(string_set, max_elmnt_size)
    comb_cov.print_outcome()


if __name__ == "__main__":
    main()
