# -*- coding: utf-8 -*-


class Scopes(object):

    LANE = 'lane'
    SAMPLE = 'sample'
    SUBPROJECT = 'subproject'


_PARAM_MAPPER = {
    Scopes.LANE:
        lambda _sub_poj: list(map(lambda lane: ":".join([Scopes.LANE, lane.identify]), _sub_poj.lanes)),
    Scopes.SAMPLE:
        lambda _sub_poj: list(map(lambda sample: ":".join([Scopes.SAMPLE, sample.identify]), _sub_poj.samples)),
    Scopes.SUBPROJECT:
        lambda _sub_poj: [":".join([Scopes.SUBPROJECT, _sub_poj.identify])]
}


class Status(object):
    """节点状态：(被阻塞) -> 可用 -> 通过/异常"""

    PASSED = 'passed'
    REACHABLE = 'reachable'
    UNREACHABLE = 'unreachable'
    BLOCKED = 'blocked'


class Vertex(object):

    def __init__(self, index, name, dependencies, resource_id, graph_id):
        """
        :type name: str
        :type dependencies: str
        """
        self.index = index
        self.name = name
        self.dependencies = dependencies
        self.resource_id = resource_id
        self.graph_id = graph_id

    def dump(self):
        return {
            "index": self.index,
            "name": self.name,
            "resource_id": self.resource_id,
            "dependencies": self.dependencies,
            "graph_id": self.graph_id
        }

    @staticmethod
    def load(vertex_info_dict):
        if not vertex_info_dict:
            return None
        return Vertex(**vertex_info_dict)

    def __str__(self):
        return "{}@graph<{}>: {}".format(self.name, self.graph_id, self.resource_id)


class Graph(object):

    def get_index_typology_sort(self):
        raise NotImplementedError

    def get_vertices(self):
        """
        :rtype: list of Vertex
        """
        raise NotImplementedError

    def get_in_degrees(self):
        raise NotImplementedError

    def get_reachable_vertices(self, vertices_status_dict=None):
        """去除已通过的顶点（状态为PASSED且入度为0），返回当前入度为0的可并发访问的顶点
        :rtype: list of int
        """
        raise NotImplementedError

    def update_vertices_status(self, vertices_status, new_vertices_status):
        """使用指定的新顶点状态更新，返回更新后的顶点状态信息。
        若new_vertices_status中的状态标记为passed但实际入度非0，则仍然标记为unreachable

        :param vertices_status: 当前的顶点状态
        :param new_vertices_status: 欲更新的（部分）顶点状态
        :return: 更新后的所有顶点状态
        """
        raise NotImplementedError

    def get_adj_vertices(self, vertex_index):
        """
        返回邻接顶点索引列表
        :param vertex_index:
        :rtype: set of int
        """
        raise NotImplementedError

    @property
    def identify(self):
        raise NotImplementedError

    def dump(self):
        """
        导出顶点和弧列表，冗余存储graph_id信息便于持久化存储
        :return:  {
            "arc_list": [{"graph_id": "", "vertex": "", "adj_vertex": ""}, ],
            "vertices": [{"graph_id": "", "index": "", "name": "", "resource_id", "dependencies": ""}, ]
        }
        """

        arc_list = []
        vertices = []
        for v in self.get_vertices():
            vertices.append(v.dump())
            for adj_vex in self.get_adj_vertices(v.index):
                arc_list.append({
                    "graph_id": self.identify,
                    "vertex": v.index,
                    "adj_vertex": adj_vex
                })

        return {
            "arc_list": arc_list,
            "vertices": vertices
        }

    def __str__(self):
        return "Graph@{}<{}>".format(self.identify, self.get_index_typology_sort())


class ArcNode(object):
    """边表结点"""

    def __init__(self, adjvex, next_arc):
        self.adjvex = adjvex
        self.next_arc = next_arc

    def __str__(self):
        return "adjNode {}".format(self.adjvex)


class _AdjListGraph(Graph):
    """邻接表"""

    def __init__(self, vertices, indegree, first_arc_list, graph_id):
        self.graph_id = graph_id
        self.vertices = vertices
        self.indegree_list = indegree  # 入度
        self.first_arc_list = first_arc_list
        topology_sort = self._topology_sorting()
        self.topology_sort = topology_sort

    def get_index_typology_sort(self):
        return self.topology_sort

    def get_vertices(self):
        return self.vertices

    def get_in_degrees(self):
        return self.indegree_list

    def _topology_sorting(self):

        topo_list = []
        vex_indegree = [x for x in self.indegree_list]
        zero_indegree = []

        for i, v in enumerate(self.get_vertices()):
            if vex_indegree[i] == 0:
                zero_indegree.append(i)
        while zero_indegree:
            i = zero_indegree.pop(-1)
            topo_list.append(i)
            arc = self.first_arc_list[i]
            # remove node(indegree == 0)
            while arc:
                # adj_vex indegree--
                vex_indegree[arc.adjvex] -= 1
                if vex_indegree[arc.adjvex] == 0:
                    zero_indegree.append(arc.adjvex)
                arc = arc.next_arc
        if len(topo_list) < len(self.vertices):
            raise RuntimeError("Illegal DAG: ring")
        return topo_list

    def get_reachable_vertices(self, vertices_status_dict=None):
        if not vertices_status_dict:
            vertices_status_dict = {}

        passable = []
        indegree_list = [i for i in self.indegree_list]
        for idx in self.topology_sort:
            if vertices_status_dict.get(idx) == Status.REACHABLE or vertices_status_dict.get(idx) == Status.BLOCKED:
                passable.append(idx)
                continue
            elif vertices_status_dict.get(idx) == Status.PASSED and indegree_list[idx] == 0:
                # 只有入度为0时才认可PASSED状态
                arc = self.first_arc_list[idx]
                while arc:
                    indegree_list[arc.adjvex] -= 1
                    arc = arc.next_arc
                continue

            if indegree_list[idx] == 0:
                passable.append(idx)
        return set(passable)

    def update_vertices_status(self, vertices_status, new_vertices_status):

        indegree = [i for i in self.indegree_list]
        final_status = {}
        for idx in self.topology_sort:
            status = new_vertices_status.get(idx) or vertices_status.get(idx) or Status.UNREACHABLE
            if status == Status.PASSED:
                if indegree[idx] == 0:
                    arc = self.first_arc_list[idx]
                    while arc:
                        indegree[arc.adjvex] -= 1
                        arc = arc.next_arc
                else:
                    status = Status.UNREACHABLE
            final_status[idx] = status
        return final_status

    def get_adj_vertices(self, vertex_index):
        arc = self.first_arc_list[vertex_index]
        result = []
        while arc:
            result.append(arc.adjvex)
            arc = arc.next_arc
        return result

    @property
    def identify(self):
        return self.graph_id


def subproject_2_dag(subproject, flow_config, graph_id=None):
    """
    :type subproject: gdmetro.models.SubProject
    :type flow_config: dict
    :type graph_id: 用于标识不同的config生成的图
    :param flow_config:
        {
            "upload": {
                "scope": "lane",
                "dependencies": null
            },

            "email_upload_finished": {
                "scope": "subproject",
                "dependencies": "upload"
            },

            "mapping": {
                "scope": "lane",
                "dependencies": "upload"
            },

            "wgs_or_wes": {
                "scope": "sample",
                "dependencies": "mapping"
            },

            "report": {
              "scope": "subproject",
              "dependencies": "wgs_or_wes"
            }
            ...
        }
    :rtype: Graph
    """
    graph_id = graph_id or subproject.identify
    vertex_list = _map_to_vertices(flow_config, subproject, graph_id)
    indegree = [0 for _ in vertex_list]
    first_arc = [None for _ in vertex_list]
    for index_1, v1 in enumerate(vertex_list):
        arc = None
        for index_2, v2 in enumerate(vertex_list):
            if index_1 == index_2:
                continue
            if v1.name == v2.dependencies and _is_include(
                    resource_id=v2.resource_id,
                    sub_resource_id=v1.resource_id,
                    dependencies_info=flow_config.get(v2.dependencies)):
                # v1 是 v2 的子集: v1 -> v2连通
                v1_to_v2 = ArcNode(adjvex=index_2, next_arc=None)
                if arc:
                    arc.next_arc = v1_to_v2
                else:
                    # noinspection PyTypeChecker
                    first_arc[index_1] = v1_to_v2
                arc = v1_to_v2
                indegree[index_2] += 1

    return _AdjListGraph(vertex_list, indegree, first_arc, graph_id)


def reload_graph(graph_info_dict):
    """
    重新导入graph结构
    :param graph_info_dict: ref => Graph.dump
    :rtype: Graph
    """
    vertices = [Vertex.load(v) for v in graph_info_dict['vertices']]
    vertices.sort(cmp=lambda v1, v2: v1.index - v2.index)
    first_arc_list = [None for _ in vertices]
    indegree = [0 for _ in vertices]
    for arc in graph_info_dict['arc_list']:
        # { "graph_id": self.identify, "vertex": v.index, "adj_vertex": adj_vex }
        v_index = arc['vertex']
        adj_v_index = arc['adj_vertex']
        indegree[adj_v_index] += 1
        arc = ArcNode(adj_v_index, None)
        if first_arc_list[v_index]:
            arc.next_arc = first_arc_list[v_index]
        # noinspection PyTypeChecker
        first_arc_list[v_index] = arc
    return _AdjListGraph(vertices, indegree, first_arc_list, vertices[0].graph_id)


def _map_to_vertices(flow_config, subproject, graph_id):
    """将输入转化为顶点列表"""
    vertex_list = []
    index = 0
    for name, desc in flow_config.items():
        scope = desc.get('scope')
        mapper = _PARAM_MAPPER.get(scope)
        if not mapper:
            raise RuntimeError("Unsupported param level: {}".format(scope))
        for resource_id in mapper(subproject):
            vex = Vertex(
                index=index,
                name=name,
                dependencies=desc.get('dependencies'),
                resource_id=resource_id,
                graph_id=graph_id
            )
            index += 1
            vertex_list.append(vex)
    return vertex_list


def _is_include(resource_id, sub_resource_id, dependencies_info):
    """判断subset_resource_id是否为resource_id的子集
    resource_id的格式 scope:<project_id>/<subproject_id>[/<sample_id>][/<lane_id>]
    """
    if not resource_id or not sub_resource_id:
        return False

    sp = resource_id.split(":")
    if len(sp) != 2:
        return False
    scope, res = sp[0], sp[1].split("/")

    sp = sub_resource_id.split(":")
    if len(sp) != 2:
        return False
    subset_scope, subset_res = sp[0], sp[1].split("/")

    if not res or not subset_res:
        return False

    if subset_scope != dependencies_info['scope']:
        return False
    for idx, value in enumerate(res):
        if value != subset_res[idx]:
            return False
    return True
