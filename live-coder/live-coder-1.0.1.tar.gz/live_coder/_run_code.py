import sys
import io

codeOut = io.StringIO()
codeErr = io.StringIO()

def run_code(code):
    sys.stdout = codeOut
    exec(code)
    sys.stdout = sys.__stdout__
    return codeOut.getvalue()
