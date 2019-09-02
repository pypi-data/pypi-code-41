import os, time

from whatap.conf.configuration import Configuration


class Configure(object):
    PCODE = 0
    dev = False
    net_udp_port = 6600
    last_loaded = 0

    @classmethod
    def init(cls, display=True):
        for key, value in Configuration.items():
            setattr(cls, key, value)
        
        m= cls.load(display)
        cls.last_loaded = int(time.time())

        return m
    
    @classmethod
    def load(cls, display=True):
        home = 'WHATAP_HOME'
        try:
            with open(os.path.join(os.environ[home],
                                   os.environ['WHATAP_CONFIG']), 'r') as f:
                for line in f:
                    line_strip = line.strip()
                    if not line_strip or line_strip.startswith('#'):
                        continue
                    try:
                        key, value = line.split('=')
                        key = key.strip()
                        value = value.strip()
                        cls.setProperty(key, value)
                    
                    except Exception as e:
                        print('WHATAP: ', e)
                        continue
        
        except Exception as e:
            from whatap import CONFIG_FILE_NAME, init_config
            init_config(home)
            return False
        else:
            return True
        finally:
            if display:
                from whatap import Logger
                Logger()
            
    @classmethod
    def getProperty(cls, key, value=None):
        if hasattr(cls, key):
            return getattr(cls, key)
        else:
            return value
    
    @classmethod
    def setProperty(cls, name, value):
        if hasattr(cls, name):
            if isinstance(getattr(cls, name), bool) and str(value) != 'true':
                value = False
        
        setattr(cls, name, value)
    
    def getStringSet(cls, key, default_value, deli):
        l = list()
        value = cls.getProperty(key, default_value)
        if value:
            for v in value.split(deli):
                l.append(v)
        return l
