# coding:utf-8

from django.template import loader

import xadmin
from xadmin.plugins.utils import get_context_dict
from xadmin.views import BaseAdminPlugin, ListAdminView


# excel 导入
class ListImportExcelPlugin(BaseAdminPlugin):
    import_excel = False

    def init_request(self, *args, **kwargs):
        return bool(self.import_excel)

    def block_top_toolbar(self, context, nodes):
        # nodes.append(
        #     loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html', context_instance=context))
        nodes.append(
            loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html', get_context_dict(context)))
        # loader.render_to_string(template_name='xadmin/excel/model_list.top_toolbar.import.html', context=context))


xadmin.site.register_plugin(ListImportExcelPlugin, ListAdminView)
