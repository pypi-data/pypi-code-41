# -*- coding: utf-8 -*-

"""全局统一的vertex activity id生成方式:
{action_name}:{project_id}/{subproject_id}/{sample_id}/{lane_id}
"""


def key_generate(action_name, project_id, subproject_id, *args):
    """
    生成 step key
    :param subproject_id:
    :param project_id:
    :param action_name: upload/report/wgs等任务名称
    :param args: sample_ID lane_ID 等信息
    :return: action_name:project_ID/subproject_ID/sample_ID...
    """
    segments = [project_id, subproject_id] + list(args)
    return action_name + ":" + '/'.join(segments)


def task_id_explode(key):
    """分解step id，默认传入的key没有问题"""
    sp = key.split(":")
    action_name = sp[0]
    segments = sp[1].split("/")
    project_id = segments[0]
    subproject_id = segments[1]
    others = segments[2:]
    return action_name, project_id, subproject_id, others


def vertex_map_2_activity_id(vertex):
    """ 统一规则，activity_id/step_id/task_id 统一使用 <action>:<resource_id> 的方式组合
    :type vertex: dag.Vertex
    :return: task_id
    """
    _, resource = vertex.resource_id.split(":")
    action = vertex.name
    return ":".join([action, resource])
