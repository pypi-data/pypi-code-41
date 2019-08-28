# -*- coding: utf-8 -*-

"""记录加载工具，从一个文本文件中加载出所有的记录
"""

import os

from . import models

__TEMPLATE = (
    "project_ID\tsubproject_ID\tproject_leader_email\t"
    "sample_ID\tLibrary_ID\tLane_ID\tFASTQ_1_path\t"
    "FASTQ_2_path\tread_length\tTotal_bases\tWES_or_WGS\t"
    "Chip_Name\tTotal_Samples\treference_buildversion\t"
    "Sequence_platform\tcloud_OUT_dir\tlocal_dir\t"
    "target_region\ttarget_host"
)

__KEY_LIST = __TEMPLATE.split('\t')


class IllegalTableError(ValueError):

    def __init__(self, message, project_leader_email):
        self.message = message
        self.project_leader_email = project_leader_email
        super(IllegalTableError, self).__init__(message)


def check_fastq_path(record):
    not_found = None
    if not os.path.exists(record.FASTQ_1_path):
        not_found = record.FASTQ_1_path
    elif not os.path.exists(record.FASTQ_2_path):
        not_found = record.FASTQ_2_path

    if not_found:
        raise IllegalTableError(
            message="The giving file path not found: {}".format(not_found),
            project_leader_email=record.project_leader_email
        )


def load_records(file_path, check_path=False):
    """
    从文件中加载数据
    :param file_path: 文件路径
    :param check_path: 是否检测Fastq_PATH
    :rtype: list of models.Record
    """
    with open(file_path, 'r') as f:
        first = f.readline().strip()
        if first.lower() != __TEMPLATE.lower():
            if ' ' in first:
                msg = "Illegal header of tsv: split by '\\t' instead of space (' ')"
            else:
                msg = ("Illegal header of tsv: \n "
                       "EXPECTED: {}\n ACTUALLY: {}".format(__TEMPLATE, first))
            project_leader_email = _guessing_the_project_leader_email(f.readline())
            raise IllegalTableError(
                message=msg,
                project_leader_email=project_leader_email
            )

        pos = 1
        records = []
        while True:
            line = f.readline().strip()
            if not line:
                break
            values = line.split('\t')
            if len(values) != len(__KEY_LIST):
                project_leader_email = _guessing_the_project_leader_email(f.readline())
                raise IllegalTableError(
                    project_leader_email=project_leader_email,
                    message="Unexpected sample record, position: {}".format(pos)
                )
            pos += 1
            record_dict = {__KEY_LIST[i]: values[i] for i in range(len(values))}

            r = models.Record(**record_dict)
            if check_path:
                check_fastq_path(record=r)
            records.append(r)
        return records


def line_to_record(line, check_path=False):
    """
    将一行记录转为Record对象
    :param line: 一行记录
    :param check_path: 是否检测Fastq_PATH
    :rtype: gdmetro.models.Record
    """
    values = line.split('\t')
    if len(values) != len(__KEY_LIST):
        raise IOError("Unexpected sample record")
    record_dict = {__KEY_LIST[i]: values[i] for i in range(len(values))}
    r = models.Record(**record_dict)
    if check_path:
        check_fastq_path(r)
    return r


def records_to_project_dict(record_list):
    """
    将records映射为project字典
    :type record_list: list of models.Record
    :return: {
            "project_name": {
                "sub_project_name": {
                    "sample_name": [lanes...]
                }
            }
        }
    :rtype: dict
    """
    projects = {}
    for record in record_list:
        lane = models.Lane(record)
        project = projects.setdefault(lane.project_ID, {})
        sub_project = project.setdefault(lane.subproject_ID, {})
        sample = sub_project.setdefault(lane.sample_ID, [])
        sample.append(lane)
    return projects


def records_to_project_objects(record_list):
    """
    :type record_list: list of models.Record
    :return: {
                "project_id/subproject_id": SubProject
             }
    """
    projects_dict = records_to_project_dict(record_list)
    projects_obj_dict = {}

    for project_id, subproject_dict in projects_dict.items():
        for subproject_id, sample_dict in subproject_dict.items():
            samples = []
            for sample_id, lanes in sample_dict.items():
                sample = models.Sample(lanes)
                samples.append(sample)
            subproject = models.SubProject(samples)
            projects_obj_dict['{}/{}'.format(project_id, subproject_id)] = subproject

    return projects_obj_dict


def _guessing_the_project_leader_email(line):
    if not line:
        return None
    values = line.split('\t')
    for v in values:
        if "@" in v:
            return v
