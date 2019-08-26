from django.conf import settings
import importlib

class DRFSettings(object):
    def __init__(self):
        self.drf_settings = {
            "HIDE_DOCS": self.get_setting("HIDE_DOCS") or False,
            "APP_NAME": self.get_setting("APP_NAME") or settings.ROOT_URLCONF.split(".")[0],
        }
        # 获取用户settings中的ERROR_CODE
        error_code = self.get_setting("ERROR_CODE") or False
        if error_code:
            #  TODO 异常处理
            ins = importlib.import_module(error_code)
            # 获取翻译
            translate = getattr(ins, "translate", None)
            # 校验translate格式 [{"desc":xxx, "data":{"key": "value"}}]
            for i in translate:
                if "desc" in i and "data" in i:
                    assert isinstance(i["data"], dict)
                else:
                    assert "desc" in i and "data" in i

            self.drf_settings['translate'] = translate
        else:
            self.drf_settings['translate'] = []

    def get_setting(self, name):
        try:
            return settings.DRF_DOCS[name]
        except:
            return None

    @property
    def settings(self):
        return self.drf_settings
