from swissarmykit.req.RequestBase import RequestBase

class BotDetect(RequestBase):

    def __init__(self):
        super().__init__()
        self.drop_proxy_conditions = []
        self.disable_detect = False

    def disable_detect_bot(self, value=True):
        self.disable_detect = value

    def _before_request(self, url):
        if self.disable_detect:
            return True

        if 'honeypot' in url.lower() or 'IsBot' in url.lower():
            raise Exception('---> WARN: ERROR: This website use honeyspot')

    def _after_request(self, response, url):
        if self.drop_proxy_conditions:
            for drop_condition in self.drop_proxy_conditions:
                if drop_condition in response.text:
                    print('WARN: drop condition %s:  %s' % (drop_condition, url))
                    # print(response.text) # debug
                    raise Exception('Drop proxy because %s' % drop_condition)

    def enable_check_bot(self):
        '''
        Becareful override by manual code
        :return:
        '''
        self.drop_proxy_conditions = ['distilIdentificationBlock', 'distil_r_captcha.html', 'captcha', 'Enter the characters you see below']

    def set_drop_proxy_conditions(self, drop_proxy_conditions: list):
        self.drop_proxy_conditions = drop_proxy_conditions

    def __str__(self):
        return str(self.drop_proxy_conditions)
