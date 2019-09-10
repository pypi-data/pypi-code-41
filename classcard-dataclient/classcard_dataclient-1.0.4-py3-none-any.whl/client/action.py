# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/4 16:48
"""
from ..utils.constants import *
from ..utils.requestutils import *
from ..utils.verification import *
from ..utils.data_req import *

logger = logging.getLogger(__name__)


class DataClient(object):
    """Data client as data transfer be used for saving data to class card server"""

    def __init__(self, config_module=None):
        """
        init DataClient
        :param config_module: config module
        """
        if config_module:
            try:
                config.from_obj(config_module)
            except Exception as e:
                logger.error("Error: set config fail, Detail: {}".format(e))

    @staticmethod
    def set_config_module(module):
        if module:
            try:
                config.from_obj(module)
            except Exception as e:
                logger.error("Error: set config fail, Detail: {}".format(e))

    @staticmethod
    def create_teacher(data):
        """
        create teacher of edtech user server.
        params: eg:
            data = {
                "name": "string", // 姓名
                "number": 0,  // 职工号
                "password": "base64",  // 登录密码(Base64加密)
                "gender": "M",  // 性别(M - 男, F - 女)
                "birthday": "string",  // 出生日期(xxxx-xx-xx)
                "email": "string",  // 邮箱
                "phone": "string",  // 电话
                "avatar": "",  // 头像
                "school": "string",  // 学校ID
                "ecard": "string",  // 一卡通卡号
                "specific": "string", // 老师个性化信息
                "description": "string" // 简介
            }
        :param data:  list or dict
        :return: code, msg
        """
        is_multi = True
        if not isinstance(data, dict) and not isinstance(data, list):
            logger.error("Error: No data or wrong data type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(data, dict):
            data = [data]
            is_multi = False
        is_valid = verify_teacher(data)
        if not is_valid:
            return ERROR_PARAMS, "数据必须属性不能为空或格式不正确。"
        pre_data = []
        for d in data:
            pre_data.append({
                "name": d.get("name"),
                "number": d.get("number"),
                "password": d.get("password"),
                "gender": d.get("gender"),
                "birthday": d.get("birthday"),
                "school": d.get("school"),
                "email": d.get("email"),
                "phone": d.get("phone"),
                "avatar": d.get("avatar"),
                "ecard": d.get("ecard"),
                "specific": d.get("specific"),
                "description": d.get("description")
            })
        code_list, msg_list = [], []
        for d in pre_data:
            code, rlt = create_teacher_req(d, school_id=d.get("school"))
            if code:
                logger.error("Error, create teacher fail, Detail: {}, Data: {}".format(rlt, d))
            code_list.append(code)
            msg_list.append(rlt)

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def create_student(data):
        """
        create student of edtech user server.
        params: eg:
            data = {
                "name": "string", // 姓名
                "number": 0,  // 职工号
                "password": "base64",  // 登录密码(Base64加密)
                "gender": "M",  // 性别(M - 男, F - 女)
                "birthday": "string",  // 出生日期(xxxx-xx-xx)
                "email": "string",  // 邮箱
                "phone": "string",  // 电话
                "avatar": "",  // 头像
                "school": "string",  // 学校ID
                "ecard": "string",  // 一卡通卡号
                "classof": "string",  // 入学年份, 级
                "graduateat": "string",  // 毕业年份, 届
                "specific": "string", // 学生个性化信息
                "section": "string", // 学生所在班级UUID
                "description": "string" // 简介
            }
        :param data:  list or dict
        :return: code, msg
        """
        is_multi = True
        if not isinstance(data, dict) and not isinstance(data, list):
            logger.error("Error: No data or wrong data type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(data, dict):
            data = [data]
            is_multi = False
        is_valid = verify_student(data)
        if not is_valid:
            return ERROR_PARAMS, "数据必须属性不能为空或格式不正确。"
        pre_data = []
        for d in data:
            pre_data.append({
                "name": d.get("name"),
                "number": d.get("number"),
                "password": d.get("password"),
                "gender": d.get("gender"),
                "birthday": d.get("birthday"),
                "school": d.get("school"),
                "email": d.get("email"),
                "phone": d.get("phone"),
                "avatar": d.get("avatar"),
                "ecard": d.get("ecard"),
                "classof": d.get("classof"),
                "graduateat": d.get("graduateat"),
                "specific": d.get("specific"),
                "section": d.get("section"),
                "description": d.get("description")
            })
        code_list, msg_list = [], []
        for d in pre_data:
            code, rlt = create_student_req(d, school_id=d.get("school"))
            if code:
                logger.error("Error, create student fail, Detail: {}, Data: {}".format(rlt, d))
            code_list.append(code)
            msg_list.append(rlt)

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def create_section(data):
        """
        create section of edtech user server.
        params: eg:
            data = {
                "name": "string", // 班级名称
                "number": 0,  // 班级编号
                "teacher": "string",  // 班主任ID
                "education": "string",  // 教育
                "category": 0,  // 类型, 0 行政班 1 其他班
                "school": "string",
                "grade": "string",  // 年级名称
                "motto": "string", // 班级宣言
                "description": "string" // 班级简介
            }

        :param data:  list or dict
        :return: code, msg
        """
        is_multi = True
        if not isinstance(data, dict) and not isinstance(data, list):
            logger.error("Error: No data or wrong data type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(data, dict):
            data = [data]
            is_multi = False
        is_valid = verify_section(data)
        if not is_valid:
            return ERROR_PARAMS, "数据必须属性不能为空或格式不正确。"
        pre_data = []
        for d in data:
            pre_data.append({
                "name": d.get("name"),
                "number": d.get("number"),
                "principal_id": d.get("teacher"),
                "education": d.get("education"),
                "school": d.get("school"),
                "category": d.get("category"),
                "grade": d.get("grade"),
                "motto": d.get("motto"),
                "description": d.get("description")
            })
        code_list, msg_list = [], []
        for d in pre_data:
            code, rlt = create_section_req(d, school_id=d.get("school"))
            if code:
                logger.error("Error, create section fail, Detail: {}, Data: {}".format(rlt, d))
            code_list.append(code)
            msg_list.append(rlt)

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def get_class_device_info(school_id, sn):
        """get class device info"""
        code, data = get_device_info(school_id=school_id, sn=sn)
        if code:
            logger.error("Error, query class device info, Detail: {}".format(data))
        return code, data

    @staticmethod
    def get_school_info(school_id):
        """get school info by school_id"""
        if not school_id:
            logger.error("Error: No query params.")
            return ERROR_PARAMS, MSG[ERROR_PARAMS]

        code, data = get_school_info(school_id=school_id)
        if code:
            logger.error("Error, query school info fail, Detail: {}".format(data))
        return code, data

    # @staticmethod
    # def create_section(data):
    #     """
    #     create section of class card server.
    #     params: eg:
    #         data = {
    #             "name": "string", // 班级名称
    #             "num": 0,  // 班级编号
    #             "export": 2019,  // 届别
    #             "entrance": 2015,  // 级别
    #             "teacher_num": "string",  // 班主任工号
    #             "education": "string",  // 教育
    #             "category": 0,  // 类型, 0 行政班 1 其他班
    #             "school": "string",
    #             "slogan": "string",  // 班级口号
    #             "grade": "string",  // 年级名称
    #             "declaration": "string", // 班级宣言
    #             "description": "string" // 班级简介
    #         }
    #
    #     :param data:  list or dict
    #     :return: code, msg
    #     """
    #     is_multi = True
    #     if not isinstance(data, dict) and not isinstance(data, list):
    #         logger.error("Error: No data or wrong data type.")
    #         return ERROR_PARAMS, "数据为空或格式不正确。"
    #     if isinstance(data, dict):
    #         data = [data]
    #         is_multi = False
    #     is_valid = verify_section(data)
    #     if not is_valid:
    #         return ERROR_PARAMS, "数据必须属性不能为空或格式不正确。"
    #     pre_data = []
    #     for d in data:
    #         pre_data.append({
    #             "name": d.get("name"),
    #             "num": d.get("num"),
    #             "export": d.get("export"),
    #             "teacher": d.get("teacher_num"),
    #             "education": d.get("education"),
    #             "entrance": d.get("entrance"),
    #             "category": d.get("category"),
    #             "school": d.get("school"),
    #             "slogan": d.get("slogan"),
    #             "grade": d.get("grade"),
    #             "declaration": d.get("declaration"),
    #             "description": d.get("description")
    #         })
    #     code_list, msg_list = [], []
    #     for d in pre_data:
    #         code, rlt = create_section_req(d, school_id=d.get("school"))
    #         if code:
    #             logger.error("Error, create section fail, Detail: {}, Data: {}".format(rlt, d))
    #         code_list.append(code)
    #         msg_list.append(rlt if code else MSG[SUCCESS])
    #
    #     if is_multi:
    #         return code_list, msg_list
    #     return code_list[0], msg_list[0]

    @staticmethod
    def create_classroom(data):
        """
        create classroom of class card server.
        params: eg:
            data = {
                "name": "string",  // 教室名称
                "mode": "string",  // 模式: {1: '普通模式', 2: '通知模式', 3: '考试模式', 4: '会议模式', 5: '视频模式'}
                "section_name": "string",  // 班级名称
                "num": "string",  // 教室编号
                "seats": 0,  // 座位数
                "category": "string",  // 教室类型, {1: '班级教室', 2: '公共教室'}
                "device_sn": "string",  // 班牌SN
                "school": "string",  // 学校uid
                "extra_info": {}, // 扩展信息json
                "building": "string",  // 教学楼
                "floor": "string"  // 楼层
            }

        :param data:  list or dict
        :return: code, msg
        """
        is_multi = True
        if not isinstance(data, dict) and not isinstance(data, list):
            logger.error("Error: No data or wrong data type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(data, dict):
            data = [data]
            is_multi = False
        is_valid = verify_classroom(data)
        if not is_valid:
            return ERROR_PARAMS, "数据必须属性不能为空或格式不正确。"
        pre_data = []
        for d in data:
            pre_data.append({
                "name": d.get("name"),
                "num": d.get("num"),
                "section": d.get("section_name"),
                "mode": d.get("mode"),
                "seats": d.get("seats"),
                "device": d.get("device_sn"),
                "category": d.get("category"),
                "school": d.get("school"),
                "building": d.get("building"),
                "floor": d.get("floor"),
                "extra_info": d.get("extra_info")
            })
        code_list, msg_list = [], []
        for d in pre_data:
            code, rlt = create_classroom_req(d, school_id=d.get("school"))
            if code:
                logger.error("Error, create classroom fail, Detail: {}, Data: {}".format(rlt, d))
            code_list.append(code)
            msg_list.append(rlt if code else MSG[SUCCESS])

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]
