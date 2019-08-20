import os
import subprocess
from .latex_document import Document
from .latex_preamble import Preamble


class SimpleLatexDocument:
    def __init__(self, preamble=None, document=None, special=None):
        self.preamble = preamble
        self.document = document
        self.special = special

    def add(self, environment):
        if isinstance(environment, Preamble):
            self.preamble = environment
        elif isinstance(environment, Document):
            self.document = environment
        else:
            raise ValueError

    def __repr__(self):
        if self.preamble:
            repr = str(self.preamble)
        if self.document:
            repr += str(self.document)
        if self.special:
            repr += str(self.special)
        return repr

    def pdf(self, directory_for_conversion, file_name_output, clean_output_directory=True, DEBUG = False):
        try:
            latex_file_path = os.path.join(
                directory_for_conversion, file_name_output)
            if not os.path.exists(directory_for_conversion):
                os.makedirs(directory_for_conversion)
            with open(latex_file_path, 'w') as latex_outfp:
                latex_outfp.write(str(self))

            os.chdir(directory_for_conversion)
            output = subprocess.check_output(["latexmk", "-pdf", latex_file_path],
                                             stderr=subprocess.STDOUT)
            if clean_output_directory:
                cleaning = subprocess.check_output(["latexmk", "-c"], stderr=subprocess.STDOUT)
                cleaning = subprocess.check_output(["rm", "-f", latex_file_path], stderr=subprocess.STDOUT)
        except (OSError, ValueError) as exc:
            raise RuntimeError
        except Exception as exc:
            print(exc)
        finally:
            if DEBUG:
                print(output.decode())
