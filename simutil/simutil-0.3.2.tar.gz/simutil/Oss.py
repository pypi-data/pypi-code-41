from Util.Env import env
import oss2
from oss2.models import BucketCors, CorsRule, BucketReferer


class Oss():
    '''
    阿里OSS服务类
    '''
    _oss_sinstance = None

    @classmethod
    def bucket(cls):
        '''
        创建bucket
        :return:bucket
        '''
        if not cls._oss_sinstance:
            cls._oss_sinstance = oss2.Bucket(
                oss2.Auth(env('OSS_ACCESS_KEY'), env('OSS_ACCESS_SECRET')),
                env('OSS_END_POINT'),
                env('OSS_BUCKET_NAME'),
            )
        return cls._oss_sinstance

    @classmethod
    def push(cls, filename, content, header={'Content-Type': 'application/json; charset=utf-8'}):
        '''
        上传文件
        :param filename: 上传文件名， 例如：'data/test.json'
        :param content: 上传的文件内容
        :return:
        '''
        return cls.bucket().put_object(filename, content, headers=header)

    @classmethod
    def rule(cls, allowed_origins=['*'], allowed_methods=['GET', 'POST', 'HEAD'], allowed_headers=['*'], max_age_seconds=600):
        '''
        处理跨域
        :param allowed_origins: 来源
        :param allowed_methods: 接受的请求方法
        :param allowed_headers: 接受的请求头
        :param max_age_seconds: 缓存时间（秒）
        :return:
        '''
        rule = CorsRule(allowed_origins=allowed_origins,
                        allowed_methods=allowed_methods,
                        allowed_headers=allowed_headers,
                        max_age_seconds=max_age_seconds)
        cls.bucket().put_bucket_cors(BucketCors([rule]))
        return cls

    @classmethod
    def referer(cls, referers=None):
        '''
        防盗链
        :param referers: ['http://www.longhash.com', 'http://api.longhash.com']
        :return: cls
        '''
        if referers is not None:
            cls.bucket().put_bucket_referer(BucketReferer(False, referers))
        else:
            cls.bucket().put_bucket_referer(BucketReferer(True, []))
        return cls

    @classmethod
    def push_file(cls, yourObjectName, yourLocalFile):
        '''
        上传文件
        :param yourObjectName: oss目录
        :param yourLocalFile: 本地目录
        :return:
        '''
        return cls.bucket().put_object_from_file(yourObjectName, yourLocalFile)

if __name__ == '__main__':
    import requests
    import json

    html = requests.get('https://longhash.oss-cn-hongkong.aliyuncs.com/data/livechart/exchage.json')
    Oss.rule().referer().push('test.json', json.dumps(html.json()))
