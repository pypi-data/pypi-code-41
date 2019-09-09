from report.accountsummary.accountsummary import AccountSummary


report = AccountSummary()


def test_gen_reports() -> None:
    text = report._gen_reports()
    for s in {
        'Stock Value',
        'Option Value',
        'Margin Used',
        'Account Value',
        '# of Symbols',
        'Profit on Stocks',
        'Profit on Options',
        'Profit on Call Writes',
        'Profit on Put Writes',
        'Symbol',
        '# of Shares',
        'Settled Profit',
    }:
        assert s in text
