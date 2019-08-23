from ofx2xlsmbr.writer.IWriterController import IWriterController
from ofx2xlsmbr.model.BankStatement import BSEncoder

import json

class BSWriterController(IWriterController):
    def write(self, data, factory, outputFilename=''):
        bStmts = []
        for bs in data:
            bStmts.append(json.dumps(bs, cls=BSEncoder))
        return bStmts