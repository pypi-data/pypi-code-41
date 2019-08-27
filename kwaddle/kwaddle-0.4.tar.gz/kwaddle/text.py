
class Text(object):
    """Simple container of text data."""

    def __init__(self, text):
        """
        Load from text.

        Parameters
        ----------
        text : str
            String of the text for some given document.
        """
        self._text = text
        self.unique_characters = list(set(text))
        self.token_to_index = {c: idx for idx, c in enumerate(self.unique_characters)}
        self.index_to_character = {idx: c for idx, c in enumerate(self.unique_characters)}

    def encode_text(self):
        """
        Encode text into a numerical representation.

        Each character within the text is converted into an integer, such that
        each unique character is represented by a different integer.

        Returns
        -------
        list of int
        """
        return [self.token_to_index[c] for c in self._text]

    @property
    def vocabulary_size(self):
        """Number of unique characters within the text."""
        return len(self.unique_characters)
