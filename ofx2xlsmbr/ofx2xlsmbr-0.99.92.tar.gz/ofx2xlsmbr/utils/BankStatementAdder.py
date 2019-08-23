from ofx2xlsmbr.model.BankStatement import BankStatement

class BankStatementAdder(object):
    def add(self, bankStatement_1: BankStatement, bankStatement_2: BankStatement, removeDuplicates = True) -> BankStatement:
        bnkStmt = BankStatement()

        bnkStmt.inflows += bankStatement_1.inflows
        bnkStmt.outflows += bankStatement_1.outflows

        if (removeDuplicates):
            for inflow in bankStatement_2.inflows:
                if inflow not in bnkStmt.inflows:
                    bnkStmt.inflows.append(inflow)

            for outflow in bankStatement_2.outflows:
                if outflow not in bnkStmt.outflows:
                    bnkStmt.outflows.append(outflow)
        else:
            bnkStmt.inflows += bankStatement_2.inflows
            bnkStmt.outflows += bankStatement_2.outflows

        return bnkStmt