

def request_params_to_dict(query_dict_obj, all_params_names=None, list_params_names=None, value_params_names=None):
    """
    QueryDict 参数对象转换
    将QueryDict参数转换为字典
    Args:
        query_dict_obj: QueryDict 对象
        all_params_names: 所有的请求参数名元组
        list_params_names: 请求参数类型为列表类型的参数名元组
        value_params_names: 请求参数类型为值类型的参数名元组

    Returns:
        参数字典
    """
    query_dict_dict = {}

    def get_params_dict(name):
        if list_params_names:
            if name in list_params_names:
                if name in query_dict_obj:
                    query_dict_dict[name] = query_dict_obj.getlist(name)
                return

        if value_params_names:
            if name in value_params_names:
                if name in query_dict_obj:
                    query_dict_dict[name] = query_dict_obj.get(name)
                return

        if name in query_dict_obj:
            if len(query_dict_obj.getlist(name)) > 1:
                query_dict_dict[name] = query_dict_obj.getlist(name)
            else:
                query_dict_dict[name] = query_dict_obj.get(name)

    if all_params_names:
        for name in all_params_names:
            get_params_dict(name)
    else:
        query_dict_list = query_dict_obj.lists()
        for key, value in query_dict_list:
            get_params_dict(key)

    return query_dict_dict

