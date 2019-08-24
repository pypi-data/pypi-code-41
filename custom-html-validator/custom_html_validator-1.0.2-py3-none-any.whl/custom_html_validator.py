from html.parser import HTMLParser

class CustomHTMLValidater(HTMLParser):
    __SINGLE_TAGS = [
        'area','base','br','col','embed',
        'hr','img','input','keygen','link',
        'meta','param','source','track','wbr'
    ]

    def __init__(self):
        HTMLParser.__init__(self)
        self.reset(True)

    def reset(self, tag_reset = False):
        HTMLParser.reset(self)
        self.__core = {
            'status': 0,
            'detail':'',
            'detected_list':[]
        }
        if tag_reset:
            self.__allowed_tags = []
        return

    def set_allowed_tags(self, __allowed_tags):
        self.__allowed_tags = __allowed_tags
        return

    def handle_starttag(self,tag,attrs):
        if self.__core['status'] == 0:
            if not tag in self.__allowed_tags:
                self.__core['status'] = -1
                self.__core['detail'] = 'not_allowed_tag'
            else:
                for attr in attrs:
                    if not attr[0] in self.__allowed_tags[tag]:
                        self.__core['status'] = -1
                        self.__core['detail'] = 'not_allowed_attr'
                        return
                detected = {
                    'tag': tag,
                    'attr': attrs,
                    'complete': False
                }
                self.__core['detected_list'].append(detected)
        return

    def handle_endtag(self,tag):
        if self.__core['status'] == 0:
            last_index = len(self.__core['detected_list']) - 1
            for index in range(last_index, -1, -1):
                data = self.__core['detected_list'][index]
                if not data['complete']:
                    if data['tag'] == tag:
                        data['complete'] = True
                        return 
                    elif data['tag'] in self.__SINGLE_TAGS:
                        data['complete'] = True
                    else:
                        break
            self.__core['status'] = -1
            self.__core['detail'] = 'Construction Error'
        return

    def close(self):
        HTMLParser.close(self)
        if self.__core['status'] == 0:
            errored = False
            for data in self.__core['detected_list']:
                if not data['complete']:
                    if data['tag'] in self.__SINGLE_TAGS:
                        data['complete'] = True
                        continue
                    self.__core['status'] = -1
                    self.__core['detail'] = 'Construction Error'
                    errored = True
                    break
            if not errored:
                self.__core['status'] = 1
                self.__core['detail'] = 'ok'
        return self.__core
