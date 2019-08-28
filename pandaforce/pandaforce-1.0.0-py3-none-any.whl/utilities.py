# Utility functions within sfpack
def __addColor(text):
    """Provides blue color and bold formatting for passed string"""
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    return ('{}{}{}{}{}'.format(BLUE,BOLD,text,END,END))

def __expectString(val):
    """Raises standard Exception message if passed value is not a string"""
    if type(val) != str:
        raise Exception('Expected string, received {}'.format(type(val)))
        
def info():
    """Displays list of primary sfpack functions"""
    print('sfpack contains the following functions:\n' +
        '  - {}:\t{}\n'.format(__addColor('convertTo18'),convertTo18.__doc__) + 
        '  - {}:\t\t{}\n'.format(__addColor('isNull'),isNull.__doc__) +
        '  - {}:\t{}'.format(__addColor('repairCasing'),repairCasing.__doc__))
    print('\nIt also contains a '+ __addColor('login') +
        ' class which initiates a connection to a Salesforce org. It contains the following methods:\n' +
        '  - {}:\t{}\n'.format(__addColor('checkObject'),login.checkObject.__doc__) + 
        '  - {}:\t\t{}\n'.format(__addColor('getdf'),login.getdf.__doc__) + 
        '  - {}:\t{}\n'.format(__addColor('getObjectFields'),login.getObjectFields.__doc__) +
        '  - {}:{}\n'.format(__addColor('getObjectFieldsDict'),login.getObjectFieldsDict.__doc__) + 
        '  - {}:\t\t{}'.format(__addColor('getReport'),login.getReport.__doc__))
    
    print('\nType \'help(function_name)\' or \'help(login.method_name)\' for additional information on each function or method')

def convertTo18(fifteenId):
    """Converts the passed Salesforce 15-digit ID to an 18-digit Id"""
    __expectString(fifteenId)
    if len(fifteenId) != 15:
        raise Exception('Expected 15 character string, received {} character string'.format(len(fifteenId)))
    elif len(sub('[a-zA-z0-9]','',fifteenId)) > 0:
        raise Exception('Passed string cannot contain any special characters (i.e. "!","@","#")')
    suffix = ''
    for i in range(0, 3):
        flags = 0
        for x in range(0,5):
            c = fifteenId[i*5+x]
            #add flag if c is uppercase
            if c.upper() == c and c >= 'A' and c <= 'Z':
                flags = flags + (1 << x)
        if flags <= 25:
            suffix = suffix + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[flags]
        else:
            suffix = suffix + '012345'[flags - 26]
    return fifteenId + suffix

def repairCasing(x18DigitId):
    """Changes 18-digit IDs that have had all character's capitalized to a Salesforce viable 18-digit Id"""
    def getBitPatterns(c):
        CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
        index = CHARS.find(c)
        result = []
        for bitNumber in range(0,5):
            result.append((index & (1 << bitNumber)) != 0)
        return result

    __expectString(x18DigitId)
    if len(x18DigitId) != 18:
        raise Exception('Expected 18 character string, received {} character string'.format(len(x18DigitId)))
    elif len(sub('[a-zA-z0-9]','',x18DigitId)) > 0:
        raise Exception('Passed string cannot contain any special characters (i.e. "!","@","#")')

    toUpper = []
    toUpper.append(getBitPatterns(x18DigitId[15:16]))
    toUpper.append(getBitPatterns(x18DigitId[16:17]))
    toUpper.append(getBitPatterns(x18DigitId[17:18]))
    toUpper = [item for sublist in toUpper for item in sublist]

    output = ''.join([x18DigitId[x].upper() if toUpper[x] else x18DigitId[x].lower() for x in range(0,15)]) + x18DigitId[15:].upper()

    return output

def isNull(val):
    """Returns boolean value for passed value indicating if it is a Null or NaN value"""
    if val == None:
        return True
    elif val != val:
        return True
    else:
        return False
        

