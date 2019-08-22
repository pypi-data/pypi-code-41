class ReturnCode():
    """
    成功
    """

    SUCCESS = "0000"
    """未查询到数据
    """

    NO_DATA = "0001"
    """失败
    """
    FAILED = "0002"

    """账号不存在或者被禁用
    """
    ACCOUNT_ERROR = "1000"

    """token异常或失效
    """
    TOKEN_ERROR = "1001"

    """接口不存在
    """
    API_NOT_EXISTS = "1002"

    '''没有接口权限
    '''
    API_NOT_PERMISSION = "1003"

    '''参数异常
    '''
    PARAMS_ERROR = "1004"

    '''没有接口权限
    '''
    API_DISABLE = "1011"

    '''异常IP
    '''
    UNKOWN_IP = "1099"

    '''黑名单IP
    '''
    BLACK_IP = "1098"

    '''系统异常
    '''
    SYSTEM_ERROR = "9999"
