"""xpaths module."""
ITALIA = {
    'chiamate': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]'
                 '/div[3]/div[1]/div[1]/div/div[1]'),
    'sms': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]'
            '/div[3]/div[1]/div[2]/div/div[1]'),
    'internet': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]'
                 '/div[2]/div[3]/div[2]/div[1]/div/div[1]'),
    'mms': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]'
            '/div[3]/div[2]/div[2]/div/div[1]')
}

ESTERO = {
    'chiamate': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]'
                 '/div[2]/div[4]/div[1]/div[1]/div/div[1]'),
    'sms': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]'
            '/div[4]/div[1]/div[2]/div/div[1]'),
    'internet': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]'
                 '/div[4]/div[2]/div[1]/div/div[1]'),
    'mms': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[4]'
            '/div[2]/div[2]/div/div[1]')
}

GENERAL_INFO = {
    'utente': ('/html/body/div[1]/div[2]/div/nav/div/div/div[2]/div[1]'),
    'id_utente': ('/html/body/div[1]/div[2]/div/nav/div/div/div[2]/div[2]'),
    'numero': ('/html/body/div[1]/div[2]/div/nav/div/div/div[2]/div[3]'),
    'credito': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]'
                '/h2/b'),
    'rinnovo': ('/html/body/div[1]/div[2]/div/div/div/div/div[2]/div[2]'
                '/div[2]')
}
