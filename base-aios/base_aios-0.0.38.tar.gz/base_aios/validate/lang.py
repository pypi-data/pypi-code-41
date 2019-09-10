import os
from configobj import ConfigObj

class Language(object):

    def __init__(self, accept_languages=[]):
        self._resource = dict()
        self.accept_languages = accept_languages

        ini_dir = os.path.join(os.getcwd(), 'base_aios', 'validate', 'languages')
        for root, dirs, files in os.walk(ini_dir):
            for file in filter(lambda x: x.endswith('.ini'), files):
                ini_file = os.path.join(root, file)
                config = ConfigObj(infile=ini_file)
                
                region = file.replace('.ini', '')
                
                lang_resources = dict()
                for section in config.sections:
                    if lang_resources.get(section) is None:
                        lang_resources.setdefault(section, dict())
                    for k in config[section]:
                        lang_resources[section][k] = config[section][k]
                
                self._resource[region] = lang_resources
            
    def _get_value(self, region, section, key):
        if key not in self._resource[region][section].keys():
            raise Exception('多语言资源文件中不存在key={}'.format(key))
        else:
            return self._resource[region][section][key]

    # ---------模块-----------------
    def req(self, key):
        return self._resource['REQ']
    
    def resp(self, key):
        """response返回值的多语言获取方法
        """
        if 'en-US' in self.accept_languages:
            return self._get_value('en-US', 'RESP', key)
        else:
            return self._get_value('zh-CN', 'RESP', key)
    
    def comm(self, key):
        """常用语的多语言获取方法
        """
        if 'en-US' in self.accept_languages:
            return self._get_value('en-US', 'COMMON', key)
        else:
            return self._get_value('zh-CN', 'COMMON', key)
    
    def mail(self, key):
        """邮件信息的多语言获取方法
        """
        if 'en-US' in self.accept_languages:
            return self._get_value('en-US', 'MAIL', key)
        else:
            return self._get_value('zh-CN', 'MAIL', key)
    # ---------模块-----------------
# lang = Language()
if __name__ == '__main__':
    lang = Language()
    
    