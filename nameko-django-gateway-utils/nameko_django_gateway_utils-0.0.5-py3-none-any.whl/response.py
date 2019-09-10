from django.http.response import JsonResponse


class RpcHttpResponse(JsonResponse):
    """
    返回RPC http response

    Args:
        data: RPC 调用返回结果
            格式：
                {
                    'data': data,
                    'code': status_code,
                    'msg': message,

                    # 分页信息
                    'prev': url/None,
                    'next': url/None,
                }
        return_format: 返回格式'json'
    """
    def __init__(self, data, *, status=None, return_format='json'):
        """
        Args:
            data: RPC 返回结果
                format:
                    {
                        'data':
                            {
                                'result': ,
                                ...
                            },
                        'code': xxx,
                        'msg': xxxxxx
                    }
            return_format: HTTP格式化输出结果
        """

        # status_code 默认值为 200
        if status is None:
            status = data['code'] if 'code' in data else 200

        # 如果result无data属性，默认为内部错误 500
        exclude_result = ['code', 'msg', 'data']
        return_result = {key: data[key] for key in data.keys() if key not in exclude_result}

        # 格式转换`msg` -> `info`
        if 'msg' in data and data['msg']:
            return_result['info'] = data['msg']

        # 将`data`对象值进行提升
        if 'data' in data and data['data']:
            return_result.update(data['data'])

        # print(return_result, data)
        super(RpcHttpResponse, self).__init__(data=return_result, status=status)
