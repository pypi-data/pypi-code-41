import logging
import datetime
from .sqlite_model import session, model_dic, ImageTemplate, ReplaceImages


class GetData:

    def __init__(self, logger):
        super(GetData, self).__init__()
        self.logger = logger
        try:
            session.commit()
        except Exception as E:
            pass

    def add(self, model, add_dic):
        add_sta = 'ok'
        if 'create_time' not in add_dic:
            create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_dic.update({'create_time': create_time})
        try:
            session.add(model(**add_dic))
        except Exception as E:
            logging.error('add fail : {}'.format(E))
            add_sta = 'Error'
        session.commit()
        return add_sta

    def get(self, model_name, key_list=None, filter_dic=None, first_or_all='all', return_model_map=True):
        try:
            session.commit()
        except Exception as E:
            commit_str = 'commit error : {}'.format(E)
            pass
        query_str = '{}'.format(model_name)
        if key_list is not None:
            query_lis = ['{}.{}'.format(model_name, x) for x in key_list]
            query_str = ', '.join(query_lis)

        filter_str = ''
        if filter_dic is not None:
            filter_lis = ['{}.{}=="{}"'.format(model_name, y, filter_dic.get(y)) for y in filter_dic]
            filter_str = ', '.join(filter_lis)

        get_str = 'session.query({query}).filter({filters}).{first_or_all}()'.\
            format(query=query_str, filters=filter_str, first_or_all=first_or_all)
        try:
            res = eval(get_str)
            if not return_model_map:
                return res
            model_map = [model_dic[model_name](**dict(zip(x.keys(), x))) for x in res]
            return model_map
        except Exception as E:
            get_sta = 'get data fail :{}'.format(E)
            logging.error(get_sta)
        return None

    def update(self, model_name, update_dic, filter_dic):
        model = model_dic.get(model_name)
        if not model:
            self.logger.error('model name not in model dict')
            return None
        try:
            update_search = self.get(model_name=model_name, filter_dic=filter_dic, return_model_map=False)
            old_updates = [x.to_dict() for x in update_search]
            del_res = self.delete_data(model_name=model_name, filter_dic=filter_dic)
            if del_res:
                add_sta = False
                for old_dic in old_updates:
                    old_dic.update(update_dic)
                    add_res = self.add(model=model, add_dic=old_dic)
                    if add_res == 'ok':
                        add_sta = True
                return add_sta
        except Exception as E:
            self.logger.error('update fail: {}'.format(E))
            return False

    def delete_data(self, model_name, filter_dic=None):
        model = model_dic.get(model_name)
        if not model:
            self.logger.error('model name not in model dict')
            return None
        del_search = self.get(model_name=model_name, filter_dic=filter_dic, return_model_map=False)
        try:
            for clo in del_search:
                session.delete(clo)
                session.commit()
            return True
        except Exception as E:
            logging.error('delete fail : {}'.format(E))
            return False

