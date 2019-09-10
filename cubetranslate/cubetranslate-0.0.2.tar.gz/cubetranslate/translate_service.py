# -*- coding:utf-8 -*-

from googletrans import Translator
from constants import SPECIAL_CASES, LANGUAGES, LANGCODES

class GoogleTranslate(object):
    def __init__(self):
        self.translator = Translator(service_urls=['translate.google.cn'])

    def _pre_process(self, src='auto', dest='en'):
        # 判断语言缩写是否正确
        if src != 'auto' and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                return 'src err'

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                return 'dest err'

        return False

    def translate(self, trans_para):
        src = trans_para[0]
        dest = trans_para[1]
        source = trans_para[2]
        para_verify = self._pre_process( src, dest)
        if para_verify == 'src err':
            return '初始语言名称输入错误。'
        elif para_verify == 'dest err':
            return '目标语言名称输入错误。'

        return self.translator.translate(source, src=src, dest=dest).text

