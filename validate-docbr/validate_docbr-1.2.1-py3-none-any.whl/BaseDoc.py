from abc import ABC


class BaseDoc(ABC):
    """Classe base para todas as classes referentes a documentos."""

    def validate(self, doc: str = '') -> bool:
        """Método para validar o documento desejado."""
        pass

    def generate(self, mask: bool = False) -> str:
        """Método para gerar um documento válido."""
        pass

    def generate_list(self, n: int = 1, mask: bool = False, repeat: bool = False) -> list:
        """Gerar uma lista do mesmo documento."""
        doc_list = []

        if n <= 0:
            return doc_list

        for i in range(n):
            doc_list.append(self.generate(mask))

        while not repeat:
            doc_set = set(doc_list)
            unique_values = len(doc_set)

            if unique_values < n:
                doc_list = list(doc_set) + self.generate_list((n-unique_values), mask, repeat)
            else:
                repeat = True

        return doc_list

    def mask(self, doc: str = '') -> str:
        """Mascara o documento enviado"""
        pass

    def _only_digits(self, doc: str = '') -> str:
        """Remove os outros caracteres que não sejam dígitos."""
        return "".join([x for x in doc if x.isdigit()])
