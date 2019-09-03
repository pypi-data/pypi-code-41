#!/usr/bin/env python
# -*- coding: utf-8 -*-


import socketio
from core.rule_db import Rule,DB_Operation,session,Rule_Category
from functools import wraps

sio = socketio.Client()

action = 'rule_public'
connected='check_rule_version'
auth = 'auth'

@sio.on('status', namespace='/chat')
def get_status(data):
    return data['message']

#身份认证
def authentication(func):
    @wraps(func)
    def inner(*args, **kwargs):
        print('正在认证')
        from gxscan import GUANXING_SECRET_KEY
        if GUANXING_SECRET_KEY:
            sio.emit(auth,{'secret_key': GUANXING_SECRET_KEY}, namespace='/chat')
            @sio.on(GUANXING_SECRET_KEY, namespace='/chat')
            def get_status(data):
                if data['message'] == 'ok':
                    print('认证完成')
                    return func(*args, **kwargs)
                else:
                    sio.disconnect()
                    raise ConnectionError('身份验证失败！')
        else:
            sio.disconnect()
            raise ConnectionError('未检测到secret_key!')
    return inner


@sio.on('message', namespace='/chat') # 运行中接受消息
def on_response(data):
    print('接收到的消息',data)
    # 同步数据
    run_sqlDB_Version(data)
    tongbubanebn(data)
    session.commit()
    # 同步版本

def tongbubanebn(data): # 存储操作记录
    db_version_id = data['db_version_id']
    db_method = data['db_method']
    db_table = data['db_table']
    db_table_id = data['db_table_id']
    db_content = data['db_content']
    db_des = data.get('db_des')
    db_o=DB_Operation(db_version_id=db_version_id,db_method=db_method,db_table=db_table,db_table_id=db_table_id,db_content=db_content,db_des=db_des)
    session.add(db_o)
    # 最后一次执行commit
    return True

def run_sqlDB_Version(data):
    db_version_id = data.get('db_version_id')
    db_method = data.get('db_method')
    db_table = data.get('db_table')
    db_table_id = data.get('db_table_id')
    db_content = eval(data.get('db_content','{}'))
    db_des = data.get('db_des')
    if db_method=='a':# 执行添加操作
        print('同步添加数据{}'.format(db_table_id))
        if db_table=='Rule': # 添加规则
            rule_name=db_content.get('rule_name')
            rule_version=db_content.get('rule_version')
            rule_tag=db_content.get('rule_tag')
            rule_method=db_content.get('rule_method')
            rule_pattern=db_content.get('rule_pattern')
            rule_join_url=db_content.get('rule_join_url')
            demo_url=db_content.get('demo_url')
            rule_founder=db_content.get('rule_founder')
            rule_des=db_content.get('rule_des')
            rule_create_time=db_content.get('rule_create_time')
            rule_update_time=db_content.get('rule_update_time')
            rule_status=db_content.get('rule_status')
            cr_add = Rule(
                id=db_table_id,rule_name=rule_name,rule_version=rule_version,rule_tag=rule_tag,
                rule_method=rule_method,rule_pattern=rule_pattern,rule_join_url=rule_join_url,
                demo_url=demo_url,rule_founder=rule_founder,rule_des=rule_des,rule_create_time=rule_create_time,rule_update_time=rule_update_time,rule_status=rule_status,
            )
            session.add(cr_add)
            # session.commit()
            return True
        elif db_table=='Rule_Category': # 添加标签
            category_name=db_content.get('category_name')
            category_des=db_content.get('category_des')
            rc_add = Rule_Category(category_name=category_name,category_des=category_des)
            session.add(rc_add)
            # session.commit()
            return True

    elif db_method=='d':# 执行删除操作
        print('同步删除数据{}'.format(db_table_id))
        if db_table == 'Rule': # 删除规则
            cr_del  = session.query(Rule).filter(Rule.id==db_table_id).first()
            if cr_del:
                session.delete(cr_del)
                # session.commit()
                return True
        elif db_table == 'Rule_Category': # 删除标签
            rc_del  = session.query(Rule_Category).filter(Rule_Category.id==db_table_id).first()
            if rc_del:
                session.delete(rc_del)
                # session.commit()
                return True

    elif db_method=='u': # 执行更新操作
        print('同步更新数据{}'.format(db_table_id))
        if db_table == 'Rule': # 更新规则
            cr_upd=session.query(Rule).filter(Rule.id==db_table_id).first()
            if cr_upd:
                cr_upd.rule_name=db_content.get('rule_name')
                cr_upd.rule_version=db_content.get('rule_version')
                cr_upd.rule_tag=db_content.get('rule_tag')
                cr_upd.rule_method=db_content.get('rule_method')
                cr_upd.rule_pattern=db_content.get('rule_pattern')
                cr_upd.rule_join_url=db_content.get('rule_join_url')
                cr_upd.demo_url=db_content.get('demo_url')
                cr_upd.rule_founder=db_content.get('rule_founder')
                cr_upd.rule_des=db_content.get('rule_des')
                cr_upd.rule_create_time=db_content.get('rule_create_time')
                cr_upd.rule_update_time=db_content.get('rule_update_time')
                if db_content.get('rule_status'):
                    cr_upd.rule_status=db_content.get('rule_status')

                # session.commit()
                return True
        elif db_table == 'Rule_Category': # 更新标签
            rc_upd=session.query(Rule_Category).filter(Rule_Category.id==db_table_id).first()
            rc_upd.category_name=db_content.get('category_name')
            rc_upd.category_des=db_content.get('category_des')
            # session.commit()
            return True

@sio.on('synchronizeDB', namespace='/chat')
def on_response(DB_data):
    # print('接受同步数据',DB_data)
    if DB_data:
        for data in DB_data:
            run_sqlDB_Version(data)
            # 添加到版本库中
            tongbubanebn(data)
        session.commit() # 最后一次commmit
    else:
        print('当前为最新版本数据库')



@sio.event(namespace='/chat')
@authentication
def connect():
    from .rule_db import init_db
    init_db() # 初始化数据库，判断数据库是否存在
    print('连接中心服务器')
    last_v_id_obj = session.query(DB_Operation).order_by(DB_Operation.db_version_id.desc()).first()
    if last_v_id_obj:
        last_v_id=last_v_id_obj.db_version_id
    else:
        last_v_id=0
    sio.emit(connected, {"version_id":last_v_id}, namespace='/chat')

@sio.event(namespace='/chat')
def disconnect():
    print("I'm disconnected!")


# try:
#     sio.connect('http://127.0.0.1:8000', namespaces=['/chat'])
# except: n
#     raise ConnectionError('无法连接服务器')






