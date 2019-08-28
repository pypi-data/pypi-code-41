# -*- coding: utf-8 -*-
"""为保持前后逻辑一致，模块中属性的命名统一使用样品信息表中的属性名，即使违反PEP8的命名规则"""

import json
import os
from abc import ABCMeta

try:
    str_type = (str, unicode)
except NameError:
    str_type = (str,)


__all__ = [
    "Record",
    "RecordAwareObject",
    "DeclaredActions",
    "StandardData",
    "Lane",
    "Sample",
    "SubProject"
]

# 一条Record记录中支持的key
_RECORD_DECLARED_KEYS = {
    'project_ID': True,
    'subproject_ID': True,
    'sample_ID': True,
    'Lane_ID': True,
    'FASTQ_1_path': True,
    'FASTQ_2_path': True,
    'WES_or_WGS': True,
    'reference_buildversion': True,
    'cloud_OUT_dir': True,
    'local_dir': True,
    'target_host': True,
    'Total_Samples': True,
    'Library_ID': True,
    'read_length': True,
    'Total_bases': True,
    'Chip_Name': True,
    'Sequence_platform': True,
    "project_leader_email": True,
    "rawdata": True,
    "target_region": True,
    "src_host": True,
    "src_region": True
}


class _InternalInsensitiveMapper(object):

    def __init__(self, **kwargs):
        self.kv = {k.lower(): v for k, v in kwargs.items()}

    def __setitem__(self, key, value):
        self.kv[key.lower()] = value

    def __getitem__(self, item):
        return self.kv.get(item.lower())

    def get(self, item):
        return self.__getitem__(item)


class DeclaredActions(object):
    UPLOAD = 'upload'
    DOWNLOAD = 'download'
    WGS = 'wgs'
    REPORT = 'report'
    MAPPING = 'mapping'
    MAIL = 'mail'
    CROSSING = 'crossing'


class _RecordAwareObject(object):

    _ORIGIN_DECLARED_KEY_NAME = _InternalInsensitiveMapper(**{k: k for k in _RECORD_DECLARED_KEYS})

    @property
    def source(self):
        """数据源"""
        raise NotImplementedError

    def __getattribute__(self, item):
        """从数据源中获取project_ID等属性"""
        try:
            return super(_RecordAwareObject, self).__getattribute__(item)
        except AttributeError:
            if self._ORIGIN_DECLARED_KEY_NAME.get(item) and self.source:
                name = self._ORIGIN_DECLARED_KEY_NAME[item]
                return getattr(self.source, name)
            else:
                raise

    def data_source(self):
        """数据源, 与source等价"""
        return self.source


RecordAwareObject = _RecordAwareObject


class Record(object):

    def __init__(self, **kwargs):
        """
        对应文件中加载的每一行记录
        :keyword project_ID: 项目id
        :keyword subproject_ID: 子项目id
        :keyword sample_ID: 样本id
        :keyword project_leader_email:
        :keyword Lane_ID:
        :keyword FASTQ_1_path: 文件本地路径
        :keyword FASTQ_2_path: 文件本地路径

        :keyword WES_or_WGS: 任务类型
        :keyword reference_buildversion:

        :keyword cloud_OUT_dir: fastq文件上传路径，云端路径格式：$cloud_OUT_dir/Rawdata/
        :keyword local_dir: report任务输出下载路径
        :keyword target_host: 下机的节点id
        :keyword target_region: 样品分析所在的域（beijing/shenzhen），值为空时则认为是默认域

        :keyword Total_Samples: 预留字段：样品总数
        :keyword Library_ID:
        :keyword read_length:
        :keyword Total_bases:
        :keyword Chip_Name:
        :keyword Sequence_platform:

        :keyword src_host: 提交样品信息表的节点
        :keyword src_region: 提交样品信息表所在的域
        """

        self.project_ID = kwargs.get('project_ID')
        self.subproject_ID = kwargs.get('subproject_ID')
        self.sample_ID = kwargs.get('sample_ID')
        self.project_leader_email = kwargs.get('project_leader_email')
        self.Lane_ID = kwargs.get('Lane_ID')
        self.FASTQ_1_path = kwargs.get('FASTQ_1_path')
        self.FASTQ_2_path = kwargs.get('FASTQ_2_path')

        self.WES_or_WGS = kwargs.get('WES_or_WGS')
        self.reference_buildversion = kwargs.get('reference_buildversion')

        self.cloud_OUT_dir = kwargs.get('cloud_OUT_dir')
        self.local_dir = kwargs.get('local_dir')
        self.target_host = kwargs.get('target_host')
        self.target_region = kwargs.get('target_region')

        self.Total_Samples = kwargs.get('Total_Samples')  # 现在不判断samples数目是否足够
        self.Library_ID = kwargs.get('Library_ID')
        self.read_length = kwargs.get('read_length')
        self.Total_bases = kwargs.get('Total_bases')
        self.Chip_Name = kwargs.get('Chip_Name')
        self.Sequence_platform = kwargs.get('Sequence_platform')

        self.src_host = kwargs.get('src_host')
        self.src_region = kwargs.get('src_region')

    def to_json(self):
        return dict(
            project_ID=self.project_ID,
            subproject_ID=self.subproject_ID,
            sample_ID=self.sample_ID,
            project_leader_email=self.project_leader_email,
            Lane_ID=self.Lane_ID,
            FASTQ_1_path=self.FASTQ_1_path,
            FASTQ_2_path=self.FASTQ_2_path,
            WES_or_WGS=self.WES_or_WGS,
            reference_buildversion=self.reference_buildversion,
            cloud_OUT_dir=self.cloud_OUT_dir,
            local_dir=self.local_dir,
            target_host=self.target_host,
            Total_Samples=self.Total_Samples,
            Library_ID=self.Library_ID,
            read_length=self.read_length,
            Total_bases=self.Total_bases,
            Chip_Name=self.Chip_Name,
            Sequence_platform=self.Sequence_platform,
            target_region=self.target_region,
            src_host=self.src_host,
            src_region=self.src_region
        )

    def __str__(self):
        value = "project_ID: {}, subproject_ID: {}".format(self.project_ID, self.subproject_ID)
        if self.sample_ID:
            value += ", sample_ID: {}".format(self.sample_ID)
        if self.Lane_ID:
            value += ", Lane_ID: {}".format(self.Lane_ID)
        return value

    @property
    def rawdata(self):
        if not self.cloud_OUT_dir:
            return None
        d = 'Rawdata/'
        if not self.cloud_OUT_dir.endswith('/'):
            d = "/" + d
        return self.cloud_OUT_dir + d


class _Expandable(object):

    @staticmethod
    def from_json(dict_info):
        """

        :type dict_info: dict
        :rtype: _Expandable
        """
        raise NotImplementedError

    def to_json(self):
        """
        :rtype: dict
        """
        raise NotImplementedError


# noinspection PyPep8Naming
class StandardData(_RecordAwareObject, _Expandable):
    """至少包含样品信息表中一条记录的标准信息"""
    __metaclass__ = ABCMeta

    @property
    def subproject_ID(self):
        raise NotImplementedError

    @property
    def project_ID(self):
        raise NotImplementedError

    @property
    def identify(self):
        raise NotImplementedError


# noinspection PyPep8Naming
class Lane(StandardData):

    def __init__(self, record_info):
        """
        :type record_info: Record
        """
        self.record_info = record_info

    @property
    def Lane_ID(self):
        return self.record_info.Lane_ID

    @property
    def FASTQ_1_path(self):
        """fastq1本地路径"""
        return self.record_info.FASTQ_1_path

    @property
    def FASTQ_2_path(self):
        """fastq2本地路径"""
        return self.record_info.FASTQ_2_path

    @property
    def subproject_ID(self):
        return self.record_info.subproject_ID

    @property
    def project_ID(self):
        return self.record_info.project_ID

    @property
    def sample_ID(self):
        return self.record_info.sample_ID

    @property
    def source(self):
        return self.record_info

    @property
    def fq1_cloud_dir(self):
        return self._build_path(self.FASTQ_1_path)

    @property
    def fq2_cloud_dir(self):
        return self._build_path(self.FASTQ_2_path)

    @property
    def identify(self):
        return "/".join([self.project_ID, self.subproject_ID, self.sample_ID, self.Lane_ID])

    def _build_path(self, path):
        cloud_out_dir = self.record_info.cloud_OUT_dir
        rawdata = 'Rawdata/'
        sub = rawdata + os.path.basename(path)
        if not cloud_out_dir.endswith('/'):
            sub = '/' + sub
        return cloud_out_dir + sub

    def __str__(self):
        return "project_ID: {}, subproject_ID: {}, sample_ID: {}, Lane_ID: {}".format(
            self.project_ID, self.subproject_ID, self.sample_ID, self.Lane_ID)

    def to_json(self):
        record = self.record_info.to_json()
        return dict(
            project_ID=record.pop("project_ID"),
            subproject_ID=record.pop("subproject_ID"),
            sample_ID=record.pop("sample_ID"),
            Lane_ID=record.pop("Lane_ID"),
            extra=json.dumps(record)
        )

    @staticmethod
    def from_json(dict_info):
        record_dict = dict(
            project_ID=dict_info.pop("project_ID", None),
            subproject_ID=dict_info.pop("subproject_ID", None),
            sample_ID=dict_info.pop("sample_ID", None),
            Lane_ID=dict_info.pop("Lane_ID", None)
        )
        extra = dict_info.pop('extra', "{}")
        extra_dict = json.loads(extra)
        record_dict.update(extra_dict)

        record_info = Record(**record_dict)
        return Lane(record_info)


# noinspection PyPep8Naming
class Sample(StandardData):

    def __init__(self, lanes):
        """
        :type lanes: list of Lane
        """
        self.lanes = lanes or []
        self._sample_id = None
        self._project_id = None
        self._subproject_id = None

        self._lane_dict = {}
        # check lane
        for lane in lanes:
            if not self._sample_id:
                self._sample_id = lane.sample_ID
                self._subproject_id = lane.subproject_ID
                self._project_id = lane.project_ID

            elif self._sample_id != lane.sample_ID \
                    or self._subproject_id != lane.subproject_ID \
                    or self._project_id != lane.project_ID:
                raise ValueError("Got different sample_id/subproject_id/project_id from lane list")

            self._lane_dict[lane.Lane_ID] = lane

    @property
    def sample_ID(self):
        return self._sample_id

    @property
    def subproject_ID(self):
        return self._subproject_id

    @property
    def project_ID(self):
        return self._project_id

    def get_lane(self, lane_id):
        return self._lane_dict.get(lane_id)

    @property
    def source(self):
        if not self.lanes:
            return None
        return self.lanes[0]

    @property
    def identify(self):
        return "/".join([self.project_ID, self.subproject_ID, self.sample_ID])

    def __str__(self):
        return "project_ID: {}, subproject_ID: {}, sample_ID: {}, lanes: {}".format(
            self.project_ID, self.subproject_ID, self.sample_ID, len(self.lanes))

    def to_json(self):
        dict_info = {
            "project_ID": self.project_ID,
            "subproject_ID": self.subproject_ID,
            "sample_ID": self.sample_ID,
            "lanes": {}
        }
        for lane in self.lanes:
            dict_info['lanes'][lane.Lane_ID] = lane.to_json()
        return dict_info

    @staticmethod
    def from_json(dict_info):

        lanes = []
        for lane_id in dict_info.setdefault('lanes', {}):
            lane_info_dict = dict_info['lanes'][lane_id]
            lane = Lane.from_json(lane_info_dict)
            lanes.append(lane)
        return Sample(lanes)


# noinspection PyPep8Naming
class SubProject(StandardData):

    def __init__(self, samples):
        """
        子项目
        :param samples: 样品列表
        :type  samples: list of Sample
        """
        self.samples = samples or []

        self._project_id = None
        self._subproject_id = None

        self._sample_dict = {}

        # check lane
        for sample in samples:
            if not self._subproject_id:
                self._subproject_id = sample.subproject_ID
                self._project_id = sample.project_ID

            elif self._subproject_id != sample.subproject_ID \
                    or self._project_id != sample.project_ID:
                raise ValueError("Got different subproject_id/project_id from sample list")
            self._sample_dict[sample.sample_ID] = sample

    @property
    def subproject_ID(self):
        return self._subproject_id

    @property
    def project_ID(self):
        return self._project_id

    @property
    def lanes(self):
        lanes = []
        for sample in self.samples:
            lanes += sample.lanes
        return lanes

    def get_sample(self, sample_id):
        return self._sample_dict.get(sample_id)

    @property
    def source(self):
        if not self.samples:
            return None
        return self.samples[0]

    @property
    def identify(self):
        return "/".join([self.project_ID, self.subproject_ID])

    def __str__(self):
        return "project_ID: {}, subproject_ID: {}, samples: {}".format(
            self.project_ID, self.subproject_ID, len(self.samples))

    def to_json(self):
        dict_info = {
            "project_ID": self.project_ID,
            "subproject_ID": self.subproject_ID,
            "samples": {}
        }

        for sample in self.samples:
            dict_info['samples'][sample.sample_ID] = sample.to_json()
        return dict_info

    @staticmethod
    def from_json(dict_info):

        samples = []
        for sample_id in dict_info.setdefault("samples", {}):
            sample_info_dict = dict_info['samples'][sample_id]
            sample = Sample.from_json(sample_info_dict)
            samples.append(sample)

        return SubProject(samples)
