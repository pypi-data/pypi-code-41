import argparse
import urllib.request
import time
import ssl
import yaml
import threading


def check_config(config):
    if config['port'] == None:
        if config['scheme'] == 'https':
            config['port'] = 443
        elif config['scheme'] == 'http':
            config['port'] = 80
        else:
            raise Exception('不支持的scheme')
    try:
        config['port'] = int(config['port'])
    except Exception as e:
        print('port必须是整数')
        raise(e)
    if config['port'] < 0 or config['port'] > 65535:
        raise Exception('port必须在0-65535中取值')
    try:
        config['cycle'] = int(config['cycle'])
    except Exception as e:
        print('cycle必须是整数')
        raise(e)
    if config['cycle'] <= 0:
        raise Exception('cycle必须是正数')
    if config['scheme'] == 'http' and (config['key'] != None or config['cert'] != None):
        raise Exception('当scheme为http时不支持设置key或cert')
    elif config['scheme'] == 'https':
        if (config['key'] != None and config['cert'] == None) or (config['key'] == None and config['cert'] != None):
            raise Exception('key和cert必须同时设置')
    else:
        raise Exception('不支持scheme = %s', config['scheme'])
    return config

def parse_config_file(path):
    configs_res = []
    try:
        with open(path, 'r') as f:
            configs = yaml.load(f)
            print('config = ', configs)
    except Exception as e:
        print('解析配置文件失败')
        raise e
    for config in configs:
        config_res = check_config(config)
        configs_res.append(config_res)
    return configs_res

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scheme', choices=['http', 'https'], default='https')
    parser.add_argument('--host')
    parser.add_argument('--port', default=443)
    parser.add_argument('--basepath', default='/')
    parser.add_argument('--client-name')
    parser.add_argument('--token')
    parser.add_argument('--cycle', default='10')
    parser.add_argument('--key')
    parser.add_argument('--cert')
    parser.add_argument('--config-file')
    args = parser.parse_args()
    config_file = args.config_file
    configs = []
    if config_file != None:
        print('config-file被指定，其他参数将被忽略')
        configs = parse_config_file(config_file)
    else:
        config = {}
        config['config_name'] = 'args'
        config['scheme'] = args.scheme
        config['host'] = args.host
        config['port'] = args.port
        config['basepath'] = args.basepath
        config['client_name'] = args.client_name
        config['token'] = args.token
        config['cycle'] = args.cycle
        config['key'] = args.key
        config['cert'] = args.cert
        configs.append(check_config(config))
    return configs

def work(config):
    url = '%s://%s:%s/%s/updateClient.action?clientid=%s&token=%s' % (config['scheme'], config['host'], config['port'], config['basepath'], config['client_name'], config['token'])
    opener = None
    if config['scheme'] == 'https' and config['key'] != None and config['cert'] != None:
        context = ssl._create_unverified_context()
        context.load_cert_chain(config['cert'], config['key'])
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
    elif config['scheme'] == 'http':
        opener = urllib.request.build_opener()
    else:
        raise Exception('不支持的scheme = %s' % config['scheme'])
    count = 0
    while True:
        print('config_name = %s, count = %d, url = %s' % (config['config_name'], count, url))
        try:
            response = opener.open(url)
            str_res = response.read().decode('utf-8')
            print('config_name = %s, count = %d, res = %s' % (config['config_name'], count, str_res))
        except Exception as e:
            print(e)
        time.sleep(config['cycle'])
        count += 1

def main():
    configs = parse_args()
    for config in configs:
        t = threading.Thread(target=work, args=(config,))
        t.setDaemon(True)
        t.start()
    while (True):
        time.sleep(60 * 60)

if __name__ == '__main__':
    main()