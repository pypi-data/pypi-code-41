from yacs.config import CfgNode as _CfgNode


class CfgNode(_CfgNode):
    def merge_from_dict(self, dic):
        list_args = []
        for k, v in dic.items():
            list_args += [k, v]
        self.merge_from_list(list_args)


def create_config_node(path, new_allowed_levels=0):
    template = CfgNode(new_allowed=new_allowed_levels != 0)
    template.merge_from_file(path)

    for node in template.values():
        if isinstance(node, CfgNode):
            set_new_allow(node, new_allowed_levels - 1)
    return template


def set_new_allow(node, steps):
    node.__dict__[CfgNode.NEW_ALLOWED] = True
    if steps > 1:
        for sub_node in node.values():
            if isinstance(sub_node, CfgNode):
                set_new_allow(sub_node, steps - 1)
