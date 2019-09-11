def checkCompareVersions(version1=None, version2=None):
    
    result =  Solution(version1, version2)
    if result > 0:
        return version1+" is greater than "+version2
    elif result < 0:
        return version1+" is less than "+version2
    elif result == 0:
        return version1+" is equal to "+version2

def Solution(version1, version2):
    
    if version1 is None and version2 is None:
        raise ValueError("checkVersions() needs 2 arguments (0 given)")
    elif version2 is None or version2 is None:
        raise ValueError("checkVersions() needs 2 arguments (1 given)")
    elif not isinstance(version1, str) or not isinstance(version2, str):
        raise ValueError("strings must be of type str")  
    version1 = [int(i) for i in version1.split(".")]
    version2 = [int(i) for i in version2.split(".")]

    len1 = len(version1)
    len2 = len(version2)

    if len1 < len2:
        version1.extend([0]*(len2-len1))
    elif len2 < len1:
        version2.extend([0]*(len1-len2))

    for i in range(len(version1)):
        if version1[i] != version2[i]:
            return version1[i]-version2[i]
    return 0