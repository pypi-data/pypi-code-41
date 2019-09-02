#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : #!/usr/bin/env python
# @Time         : 2019-08-29 19:20
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import os
import joblib
from sanic import Sanic
from sanic.response import html, json, redirect, text, file, file_stream
from .ModelPredictor import ModelPredictor
from traceback import format_exc  # https://www.cnblogs.com/klchang/p/4635040.html

checkpoint = os.environ['--checkpoint']  # 绝对路径

# os.sys.path.append(checkpoint)

get_path = lambda path: os.path.join(checkpoint, path)

magic_app = Sanic(__name__)
mp = ModelPredictor()

# 存模型及预处理：{"sklearn": [(model, feature_transformer)]}
magic_model_maps = {}


@magic_app.route("/upload", methods=['GET', 'POST'])
async def upload(request):
    """upload and update model_maps
    files = {'model': open('sklearn_lr_demo.model', 'rb'),
             'feature_transformer': open('sklearn_lr_demo.py', 'rb')}
    requests.get("http://0.0.0.0:8000/upload", files=files)
    """
    output = {}
    try:
        model = request.files.get('model')  # 必须不为空
        feature_transformer = request.files.get('feature_transformer')  # 可为空

        model_type = model.name.split("_")[0]

        # 存及加载模型
        model_path = get_path(model.name)
        feature_transformer_path = get_path(feature_transformer.name)

        # 存及导入预处理脚本: 注意: 上下文模型会导致数据丢失
        with open(model_path, 'wb') as f1, open(feature_transformer_path, 'wb') as f2:
            f1.write(model.body)
            f2.write(feature_transformer.body)

            print("*" * 10, model_path)
            print("*" * 10, model_type)

            # predict = mp.predictor(model_path, model_type) # TODO: 传输有损失？？？
            model_path="/Users/yuanjie/Desktop/Projects/Python/tql-App/model_update/checkpoint/sklearn_lr_demo.model"
            predict = joblib.load(model_path).predict_proba
            print("*" * 10, predict)
            print("*" * 10, feature_transformer.name[:-3])

            import importlib
            print("*" * 10, checkpoint)
            os.sys.path.append('/Users/yuanjie/Desktop/Projects/Python/tql-App/model_update/checkpoint')
            os.sys.path.append('/Users/yuanjie/Desktop/Projects/Python/tql-App/model_update/DATA') # TODO: 传输有损失？？？



            feature_transform = importlib.import_module('sklearn_lr_demo').feature_transform


            # feature_transform = __import__("sklearn_lr_demo", globals(), locals(), [], 0).feature_transform # TODO: 无法导入
            print(feature_transform)

            # 存模型及预处理函数
            print(magic_model_maps)
            magic_model_maps[model.name] = (predict, feature_transform)

        return json({"Status": 1})

    except Exception as e:
        output['Error'] = format_exc().strip()

        return json(output)  # 1 为成功


@magic_app.route('/checkpoint/<file_name>')
async def handle_request(request, file_name):
    try:
        return await file_stream(get_path(file_name))
    except Exception as e:
        print(e)
        return text(os.popen(f"ls {checkpoint}").read())

if __name__ == '__main__':
    print(__import__("sklearn_lr_demo").feature_transform)