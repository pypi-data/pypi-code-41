from .internal.joinWith import joinWith


def toWrittenList(aList):
    andSeparated = aList[-2:]
    commaSeparated = aList[:-2]
    commaSeparated.append(joinWith(" and ")(andSeparated))
    return joinWith(", ")(commaSeparated)
