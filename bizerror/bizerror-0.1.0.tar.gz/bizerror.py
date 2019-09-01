import json

# ####################################################################
# 异常类型
# ####################################################################
class BizError(RuntimeError):
    """业务异常。
    """
    CODE = 1001001000
    MESSAGE = "未定义的异常！"

    def __init__(self, message=None):
        message = message or self.MESSAGE
        super().__init__(self.CODE, message)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return json.dumps({
            "code": self.args[0],
            "message": self.args[1]
        }, ensure_ascii=False)

    @property
    def code(self):
        return self.args[0]

    @property
    def message(self):
        return self.args[1]

    @property
    def json(self):
        return {
            "code": self.code,
            "message": self.message,
        }

class OK(BizError):
    CODE = 0
    MESSAGE = "OK"

class SysError(BizError):
    CODE = 1001000000
    MESSAGE = "系统相关异常。"

class HttpError(BizError):
    CODE = 1001010000
    MESSAGE = "HTTP协议相关异常。"

class ConfigError(BizError):
    CODE = 1001020000
    MESSAGE = "配置相关异常。"

class DataError(BizError):
    CODE = 1001030000
    MESSAGE = "数据相关异常。"

class AuthError(BizError):
    CODE = 1001040000
    MESSAGE = "认证相关异常。"

class TypeError(BizError):
    CODE = 1001050000
    MESSAGE = "数据类型相关异常。"

class ParamError(BizError):
    CODE = 1001060000
    MESSAGE = "参数相关异常。"

class FormError(BizError):
    CODE = 1001070000
    MESSAGE = "表单相关异常。"

class LogicError(BizError):
    CODE = 1001080000
    MESSAGE = "业务逻辑相关异常。"

# ####################################################################
# 系统相关异常。
# ####################################################################

class UndefinedError(SysError):
    CODE = 1001000001
    MESSAGE = "未定义的异常！"

# ####################################################################
# HTTP协议相关异常。
# ####################################################################

class RequestExpired(BizError):
    CODE = 1001010001
    MESSAGE = "请求已过期！"

class NotSupportedHttpMethod(BizError):
    CODE = 1001010002
    MESSAGE = "不支持的请求方法！"

# ####################################################################
# 数据相关异常。
# ####################################################################

class MissingConfigItem(ConfigError):
    CODE = 1001020001
    MESSAGE = "缺少必要的配置项！"

# ####################################################################
# 数据相关异常。
# ####################################################################

class TargetNotFound(DataError):
    CODE = 1001030001
    MESSAGE = "没有找到目标对象！"


# ####################################################################
# 认证相关异常。
# ####################################################################

class AccountLockedError(AuthError):
    CODE = 1001040001
    MESSAGE = "帐号被锁定，请联系管理员！"

class AccountTemporaryLockedError(AuthError):
    CODE = 1001040002
    MESSAGE = "登录失败次数超过上限，帐号被临时锁定！"

class UserPasswordError(AuthError):
    CODE = 1001040003
    MESSAGE = "帐号或密码错误，请重试！"

class AppAuthFailed(AuthError):
    CODE = 1001040004
    MESSAGE = "应用认证失败！"

class TsExpiredError(AuthError):
    CODE = 1001040005
    MESSAGE = "时间戳已失效。"

class AccountDisabledError(AuthError):
    CODE = 1001040006
    MESSAGE = "帐号已禁用，请联系管理员！"

class AccountStatusError(AuthError):
    CODE = 1001040007
    MESSAGE = "帐号状态异常，请联系管理员处理！"

class AccountRemovedError(AuthError):
    CODE = 1001040008
    MESSAGE = "帐号已删除！"

# ####################################################################
# 格式相关异常。
# ####################################################################


class CastToIntegerFailed(TypeError):
    CODE = 1001050001
    MESSAGE = "转化整数型数据失败！"

class CastToFloatFailed(TypeError):
    CODE = 1001050002
    MESSAGE = "转化浮点型数据失败！"

class CastToNumbericFailed(TypeError):
    CODE = 1001050003
    MESSAGE = "转化数值型数据失败！"

class CastToBooleanFailed(TypeError):
    CODE = 1001050004
    MESSAGE = "转化布尔型数据失败！"

class CastToStringFailed(TypeError):
    CODE = 1001050005
    MESSAGE = "转化字符串型数据失败！"

class ParseJsonError(TypeError):
    CODE = 1001050006
    MESSAGE = "Json转化异常！"

# ####################################################################
# 参数相关异常。
# ####################################################################


class MissingParameter(ParamError):
    CODE = 1001060001
    MESSAGE = "必要参数缺失！"

class BadParameter(ParamError):
    CODE = 1001060002
    MESSAGE = "参数值有误！"

class BadParameterType(ParamError):
    CODE = 1001060003
    MESSAGE = "参数类型有误！"

# ####################################################################
# 表单相关异常。
# ####################################################################

class CaptchaOnlyAllowedOnce(FormError):
    CODE = 1001070001
    MESSAGE = "验证码不允许重复使用！"

class CaptchaValidateFailed(FormError):
    CODE = 1001070002
    MESSAGE = "图片验证码校验失败！"
