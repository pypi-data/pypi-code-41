import logging
import pickle
import re
import sys
import threading
import time
from inspect import isfunction
from dill.source import getsource as gs
import datetime

import prettytable as pt
import psutil

from .sqlite_model import SxclzySchedule
from .sqlite_orm import GetData
from .Dict import Dict


class Sxclzy:

    def __init__(self, log_level=None):
        self._lock = threading.Lock()
        log_level = logging.INFO if log_level is None else log_level
        self._logger = self._set_logger(log_level)
        self._spider_task_dic = dict()
        self.MEMORY_THRESHOLD = 99
        self.CPU_THRESHOLD = 99
        self._db = GetData(self._logger)
        self._keys_set = {
            "year",
            "month",
            "day",
            "week",
            "hour",
            "minute",
            "second",
            "y",
            "m",
            "d",
            "w",
            "H",
            "M",
            "S",
        }
        self._keys_dic = {
            "y": "year",
            "m": "month",
            "d": "day",
            "w": "week",
            "H": "hour",
            "M": "minute",
            "S": "second",
        }
        self._keys_set_lis = [[y for y in x] for x in self._keys_set]
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._logger.info('initialize at: {}'.format(time_now))

    def start(self, exit_if_no_missions=True):
        while True:
            self._task_scheduler(exit_if_no_missions)
            time.sleep(1)

    def add_schedule(self, name, func, schedule, run_times=None, args=None, status=1, overwrite_if_exist=True):
        self._lock.acquire()
        names_in_db = {x.get('name') for x in self._get_db_schedule(filed=['name'])}
        self._lock.release()
        if not name or not isinstance(name, str):
            raise ValueError('name expect str type, not {}'.format(self._type_str(name)))
        if name in names_in_db:
            if not overwrite_if_exist:
                raise ValueError('the name {} is already exist, please use another one'.format(name))
            else:
                self._lock.acquire()
                self._db.delete_data(model_name='SxclzySchedule', filter_dic={'name': name})
                self._lock.release()
        if not isfunction(func):
            raise ValueError('func expect a function, not {}'.format(self._type_str(func)))
        if not isinstance(status, int):
            raise ValueError('status expect int, not {}'.format(self._type_str(status)))
        if not isinstance(args, dict):
            raise ValueError('args expect dict, not {}'.format(self._type_str(args)))
        if isinstance(schedule, dict):
            if run_times is not None and not isinstance(run_times, int):
                raise ValueError('the run_times expect a int type num, not {}'.format(self._type_str(run_times)))
            for key in schedule.keys():
                if key not in self._keys_set:
                    mean_key = self._check_key(key)
                    raise ValueError('found "{}" in your schedule dict, maybe you mean "{}"'.format(key, mean_key))
                if key in self._keys_dic:
                    val = schedule.pop(key)
                    schedule[self._keys_dic[key]] = val
            func_name = re.findall('<function ([^ ]+) ', str(func))[0]
            func_dump = pickle.dumps(self._check_func(gs(func)))
            schedule_dic_dump = pickle.dumps(schedule)
            args_dump = pickle.dumps(args) if args is not None else ''
            run_times = 3471292800 if run_times is None else run_times
            self._db.add(model=SxclzySchedule,
                         add_dic={'name': name,
                                  'func_name': func_name,
                                  'func': func_dump,
                                  'schedule': schedule_dic_dump,
                                  'run_times': run_times,
                                  'args': args_dump,
                                  'status': status})
            self._logger.info('add success')
        elif isinstance(schedule, str):
            if not re.findall('(2[0-9]{3}),(0?[0-9]|1[0-2]),(0?[1-9]|[12][0-9]|3[01]),([0-1]?[0-9]|2[0-3]),(0?[0-9]|['
                              '1-5][0-9]),(0?[0-9]|[1-5][0-9])', schedule):
                raise ValueError('sth wrong with your schedule setting, require a str type like : 2019,09,13,13,24,00')
            func_name = re.findall('<function ([^ ]+) ', str(func))[0]
            func_dump = pickle.dumps(self._check_func(gs(func)))
            schedule_dic_dump = pickle.dumps(schedule)
            args_dump = pickle.dumps(args) if args is not None else ''
            run_times = 3471292800 if run_times is None else run_times
            self._db.add(model=SxclzySchedule,
                         add_dic={'name': name,
                                  'func_name': func_name,
                                  'func': func_dump,
                                  'schedule': schedule_dic_dump,
                                  'run_times': run_times,
                                  'args': args_dump,
                                  'status': status})
            self._logger.info('add success')
        else:
            raise ValueError('schedule_dic expect a dict, not {}'.format(self._type_str(schedule)))

    def get_schedules(self, print_pretty=False):
        filed = ['id', 'name', 'func_name', 'func', 'schedule', 'args', 'status', 'create_time']
        self._lock.acquire()
        schedule_lis = self._get_db_schedule(filed=filed, decode_data=True)
        self._lock.release()
        if print_pretty:
            self._print_out(schedule_lis)
        return schedule_lis

    def clear_schedules(self, names=None):
        if isinstance(names, str):
            names = [names]
        self._lock.acquire()
        names_in_db = {x.get('name') for x in self._get_db_schedule(filed=['name'])}
        self._lock.release()
        names = names_in_db if names is None else names
        for name in names:
            if name in names_in_db:
                self._lock.acquire()
                self._db.delete_data(model_name='SxclzySchedule', filter_dic={'name': name})
                self._lock.release()
            else:
                self._logger.warning('no such name in db : {}'.format(name))
        self._logger.info('schedules clear up: {}'.format(str(list(names))))

    def count_down(self, data_time, time_format='y-m-d H:M:S'):
        str_location = self._locate_str(raw_str=data_time, method=time_format)
        dic = Dict(str_location)
        time_dic = {
            'year': dic.gets(['y', 'Y', '年'], '*'),
            'month': dic.gets(['m', '月'], '*'),
            'day': dic.gets(['d', '日'], '*'),
            'week': dic.gets(['w', 'W', '星期'], '*'),
            'hour': dic.gets(['H', 'h', '时'], '*'),
            'minute': dic.gets(['M', '分'], '*'),
            'second': dic.gets(['S', '秒'], '*'),
        }
        next_time_sep = self._cal_time_sep(**time_dic)
        return next_time_sep

    def _get_db_schedule(self, filed=None, decode_data=False):
        filed = ['name', 'func_name', 'func', 'schedule', 'run_times', 'args', 'status'] if filed is None else filed
        filed = set(filed)
        filed.add('status')
        filed = list(filed)
        db_result = self._db.get(model_name='SxclzySchedule',
                                 key_list=filed)
        schedule_list = list()
        if db_result:
            for x in db_result:
                if x.status != 0:
                    dic = dict()
                    for k in filed:
                        dic[k] = eval('x.{}'.format(k))
                        if decode_data and k in {'func', 'schedule', 'args'}:
                            dic[k] = pickle.loads(eval('x.{}'.format(k)))
                    schedule_list.append(dic)
        return schedule_list

    def _task_scheduler(self, exit_if_no_missions):
        self._lock.acquire()
        schedule_list_raw = self._get_db_schedule()
        self._lock.release()
        s_sta = False
        if schedule_list_raw:
            for each_schedule in schedule_list_raw:
                run_times = each_schedule.get('run_times')
                if int(run_times) > 0:
                    schedule = each_schedule.get('schedule')
                    schedule = pickle.loads(schedule)
                    name = each_schedule.get('name')
                    s_sta = True
                    try:
                        if isinstance(schedule, dict):
                            next_time_sep = self._cal_time_sep(**schedule)
                        else:
                            next_time_sep = self._cal_time_sep(schedule_str=schedule, is_str=True)
                        next_time_sep = int(next_time_sep) + 1
                        if next_time_sep > 1:
                            each_schedule['schedule'] = next_time_sep
                            each_schedule['func'] = pickle.loads(each_schedule.get('func'))
                            each_schedule['args'] = pickle.loads(each_schedule.get('args'))
                            self._lock.acquire(blocking=True)
                            if self._spider_task_dic.get(name) != 'waiting':
                                self._spider_task_dic[name] = 'waiting'
                                t = threading.Thread(target=self._runner, args=(each_schedule,))
                                try:
                                    t.start()
                                except Exception as E:
                                    self._logger.warning('function schedule error: {}'.format(E))
                            self._lock.release()
                    except ValueError:
                        self._logger.error('schedule error, please check the database')
        if not s_sta:
            self._logger.info('no missions')
            if exit_if_no_missions:
                self._logger.info('system exit')
                sys.exit(0)

    def _runner(self, dic):
        status = int(dic.pop('status'))
        func_code = dic.get('func')
        exec(func_code)
        func_name = dic.get('func_name')
        name = dic.get('name')
        args = dic.get('args')
        wait_time = dic.get('schedule')
        self._logger.info('function {} is waiting, countdown {}s'.format(name, wait_time))
        time.sleep(wait_time - 1)
        run_status = None
        if status == 1:
            another_wait_time = 0
            while not self._is_system_ok():
                self._logger.warning('system is fully functioning, wait another 2 seconds to run schedule')
                time.sleep(2)
                another_wait_time += 3
                if another_wait_time >= (wait_time - 10):
                    self._logger.warning('wait too long, cancel the job')
                    self._lock.acquire(blocking=True)
                    self._spider_task_dic[name] = run_status
                    self._run_countdown(name=name)
                    self._lock.release()
                    return None
            eval(func_name + '(**args)')
            run_status = 'ok'
        elif status == 2:
            eval(func_name + '(**args)')
            run_status = 'ok'
        elif status == 3:
            eval(func_name + '(**args)')
            run_status = 'ok'
        else:
            eval(func_name + '(**args)')
            run_status = 'ok'

        self._lock.acquire(blocking=True)
        self._run_countdown(name=name)
        self._spider_task_dic[name] = run_status
        self._lock.release()

    def _cal_time_sep(self,
                      year='*',
                      month='*',
                      day='*',
                      week='*',
                      hour='*',
                      minute='*',
                      second='*',
                      schedule_str=None,
                      is_str=False
                      ):
        """
            "%Y-%m-%d %H:%M:%S %w"
        """
        if is_str:
            s = [int(x.strip()) for x in schedule_str.split(',')]
            time_sep = (datetime.datetime(s[0], s[1], s[2], s[3], s[4], s[5]) - datetime.datetime.now()).total_seconds()
            return time_sep
        y = int(time.strftime("%Y", time.localtime()))
        if year != '*' and '*' in year:
            y = int(year.split('/')[-1]) + y
        elif year.isdigit():
            y = int(year)

        if week == '*':
            m = int(time.strftime("%m", time.localtime()))
            if month != '*' and '*' in month:
                m_raw = int(month.split('/')[-1])
                if m_raw >= 12:
                    raise ValueError('month value is too large, please set the year instead')
                m = m_raw + m
                if m > 12:
                    y += m // 12
                    m = m % 12
            elif month.isdigit():
                m = int(month)

            days_in_this_month = self._how_many_days_in_this_month(y, m)
            d = int(time.strftime("%d", time.localtime()))
            if day != '*' and '*' in day:
                d_raw = int(day.split('/')[-1])
                if d_raw > days_in_this_month:
                    raise ValueError('day value is too large, please set the month or the year instead')
                d = d_raw + d
                if d > days_in_this_month:
                    d = d - days_in_this_month
                    m += 1
                    if m > 12:
                        y += 1
                        m = m - 12
            elif day.isdigit():
                d = int(day)

            days_in_this_month = self._how_many_days_in_this_month(y, m)
            H = int(time.strftime("%H", time.localtime()))
            if hour != '*' and '*' in hour:
                H_raw = int(hour.split('/')[-1])
                if H_raw > 24:
                    raise ValueError('hour value is too large, please set the day instead')
                H = H_raw + H
                if H >= 24:
                    H = H - 24
                    d += 1
                    if d > days_in_this_month:
                        d = d - days_in_this_month
                        m += 1
                        if m > 12:
                            y += 1
                            m = m - 12
            elif hour.isdigit():
                H = int(hour)

            days_in_this_month = self._how_many_days_in_this_month(y, m)
            M = int(time.strftime("%M", time.localtime()))
            if minute != '*' and '*' in minute:
                M_raw = int(minute.split('/')[-1])
                if M_raw > 60:
                    raise ValueError('minute value is too large, please set the hour instead')
                M = M_raw + M
                if M >= 60:
                    M = M - 60
                    H += 1
                    if H >= 24:
                        H = H - 24
                        d += 1
                        if d > days_in_this_month:
                            d = d - days_in_this_month
                            m += 1
                            if m > 12:
                                y += 1
                                m = m - 12
            elif minute.isdigit():
                M = int(minute)

            days_in_this_month = self._how_many_days_in_this_month(y, m)
            S = int(time.strftime("%S", time.localtime()))
            if second != '*' and '*' in second:
                S_raw = int(second.split('/')[-1])
                if S_raw > 60:
                    raise ValueError('second value is too large, please set the minute instead')
                S = S_raw + S
                if S >= 60:
                    S = S - 60
                    M += 1
                    if M >= 60:
                        M = M - 60
                        H += 1
                        if H >= 24:
                            H = H - 24
                            d += 1
                            if d > days_in_this_month:
                                d = d - days_in_this_month
                                m += 1
                                if m > 12:
                                    y += 1
                                    m = m - 12
            elif second.isdigit():
                S = int(second)
            time_sep = eval(
                "(datetime.datetime({},{},{}, {},{},{}) - datetime.datetime.now()).total_seconds()".format(y, m, d, H,
                                                                                                           M, S))

        else:
            week_in_this_year = int(time.strftime("%U", time.localtime()))
            w = int(time.strftime("%w", time.localtime()))
            if '*' in week:
                w_raw = int(week.split('/')[-1])
                if w_raw >= 7:
                    raise ValueError('week value is too large, please set the day or the month instead')
                if w_raw < w:
                    week_in_this_year += 1
                w = w_raw
                if week_in_this_year > 53:
                    y += 1
                    week_in_this_year = week_in_this_year - 53

            elif week.isdigit():
                w = int(week)
                if int(week) < w:
                    week_in_this_year += 1

            H = int(time.strftime("%H", time.localtime()))
            if hour != '*' and '*' in hour:
                H_raw = int(hour.split('/')[-1])
                if H_raw >= 24:
                    raise ValueError('hour value is too large, please set the day instead')
                H = H_raw + H
                if H >= 24:
                    H = H - 24
                    w += 1
                    if w >= 7:
                        w = w - 7
                        week_in_this_year += 1
                        if week_in_this_year > 53:
                            y += 1
                            week_in_this_year = week_in_this_year - 53
            elif hour.isdigit():
                H = int(hour)

            M = int(time.strftime("%M", time.localtime()))
            if minute != '*' and '*' in minute:
                M_raw = int(minute.split('/')[-1])
                if M_raw >= 60:
                    raise ValueError('minute value is too large, please set the hour instead')
                M = M_raw + M
                if M >= 60:
                    M = M - 60
                    H += 1
                    if H >= 24:
                        H = H - 24
                        w += 1
                        if w > 7:
                            w = w - 7
                            week_in_this_year += 1
                            if week_in_this_year > 53:
                                y += 1
                                week_in_this_year = week_in_this_year - 53
            elif minute.isdigit():
                M = int(minute)

            S = int(time.strftime("%S", time.localtime()))
            if second != '*' and '*' in second:
                S_raw = int(second.split('/')[-1])
                if S_raw >= 60:
                    raise ValueError('second value is too large, please set the minute instead')
                S = S_raw + S
                if S >= 60:
                    S = S - 60
                    M += 1
                    if M >= 60:
                        M = M - 60
                        H += 1
                        if H >= 24:
                            H = H - 24
                            w += 1
                            if w > 7:
                                w = w - 7
                                week_in_this_year += 1
                                if week_in_this_year > 53:
                                    y += 1
                                    week_in_this_year = week_in_this_year - 53
            elif second.isdigit():
                S = int(second)
            if S >= 60:
                S = S - 60
                M += 1
                if M >= 60:
                    M = M - 60
                    H += 1
                    if H >= 24:
                        H = H - 24
                        w += 1
                        if w > 7:
                            w = w - 7
                            week_in_this_year += 1
                            if week_in_this_year > 53:
                                y += 1
                                week_in_this_year = week_in_this_year - 53
            m, d = self._get_month_and_days_by_week(year=y, week_in_this_year=week_in_this_year, week=w)
            time_sep = eval(
                "(datetime.datetime({},{},{}, {},{},{}) - datetime.datetime.now()).total_seconds()".format(y, m, d, H,
                                                                                                           M, S))
        return time_sep

    def _is_system_ok(self):
        is_pass = True
        cpu_list = psutil.cpu_percent(interval=1, percpu=True)
        memory_percent = psutil.virtual_memory().percent
        if cpu_list and memory_percent:
            is_cpu_ok = True
            if min(cpu_list) > self.CPU_THRESHOLD:
                is_cpu_ok = False
            is_memo_ok = True
            if memory_percent > self.MEMORY_THRESHOLD:
                is_memo_ok = False
            if not is_cpu_ok or not is_memo_ok:
                is_pass = False
        return is_pass

    def _check_key(self, key):
        key_lis = [x for x in key]
        count_dic = dict()
        for ksl in self._keys_set_lis:
            o_key = ''.join(ksl)
            score = 0
            for k in key_lis:
                if k in ksl:
                    score += 1
            count_dic[o_key] = score
        best_math = sorted(count_dic, key=count_dic.__getitem__, reverse=True)[0]
        return best_math

    def _run_countdown(self, name):
        name_and_runtimes_in_db = self._get_db_schedule(filed=['name', 'run_times'])
        run_time_in_db = [x.get('run_times') for x in name_and_runtimes_in_db if name == x.get('name')][
            0] if name_and_runtimes_in_db else 0
        if run_time_in_db > 0:
            rt = int(run_time_in_db) - 1
            self._db.update(model_name='SxclzySchedule',
                            update_dic={'run_times': rt},
                            filter_dic={'name': name})

    @staticmethod
    def _locate_str(raw_str, method, return_as_list=False):
        raw_str = raw_str.strip()
        method = method.strip()
        new_sep_str = '^>^ sep ^<^'
        method_lis = re.sub('([^\u4e00-\u9fa5a-zA-Z]+)', new_sep_str, method).split(new_sep_str)
        sep_str = re.findall('([^\u4e00-\u9fa5a-zA-Z]+)', method)
        sep_lis = list(set(sep_str))
        sep_index_set = set()
        raw_str_lis = [x for x in raw_str]
        for sep in sep_lis:
            sep_index = 0
            while True:
                if sep_index < 0:
                    break
                sep_index = raw_str.find(sep, sep_index + 1)
                if sep_index > 0:
                    sep_index_set.add(sep_index)

        for sep_i in sep_index_set:
            raw_str_lis[sep_i] = new_sep_str
        new_lis = ''.join(raw_str_lis).split(new_sep_str)
        if return_as_list:
            return new_lis
        new_dic = {n: v for n, v in zip(method_lis, new_lis)}
        return new_dic

    @staticmethod
    def _check_func(func_str):
        func_lis = func_str.split('\n')
        sp = re.findall('( *)def ', func_lis[0])[0]
        sps = len(sp)
        new_func_lis = list()
        for i in func_lis:
            new_func_lis.append(i[sps:])
        new_func_str = '\n'.join(new_func_lis)
        return new_func_str

    @staticmethod
    def _set_logger(log_level=logging.INFO):
        logger = logging.getLogger("logger")

        handler1 = logging.StreamHandler()
        # handler2 = logging.FileHandler(filename="test.log")

        logger.setLevel(log_level)
        handler1.setLevel(log_level)
        # handler2.setLevel(log_level)

        # formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        formatter = logging.Formatter("%(asctime)s >>> %(message)s")
        handler1.setFormatter(formatter)
        # handler2.setFormatter(formatter)

        logger.addHandler(handler1)
        # logger.addHandler(handler2)
        return logger

    @staticmethod
    def _set_log():
        logging.basicConfig()
        return logging

    @staticmethod
    def _get_month_and_days_by_week(year, week_in_this_year, week):
        days = week_in_this_year * 7 + week
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            Fe = 29
        else:
            Fe = 28
        month_lis = [31, Fe, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        month_count = 1
        days_count = 0
        for month_days in month_lis:
            days = days - month_days
            if days > 0:
                month_count += 1
            elif days == 0:
                days_count = 0
                month_count += 1
                break
            else:
                days_count = days + month_days
                break
        return [month_count, days_count]

    @staticmethod
    def _how_many_days_in_this_month(y, m):
        if m in (1, 3, 5, 7, 8, 10, 12):
            days = 31
        elif m in (4, 6, 9, 11):
            days = 30
        else:
            if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
                days = 29
            else:
                days = 28
        return days

    @staticmethod
    def _print_out(lis):
        filed = ['id', 'name', 'func_name', 'func', 'schedule', 'args', 'status', 'create_time', ]
        tb = pt.PrettyTable(field_names=filed)
        for row_dic in lis:
            show_row = list()
            show_row.append(row_dic.get('id'))
            show_row.append(row_dic.get('name'))
            show_row.append(row_dic.get('func_name'))
            show_row.append(row_dic.get('func'))
            show_row.append(row_dic.get('schedule'))
            show_row.append(row_dic.get('args'))
            show_row.append(row_dic.get('status'))
            show_row.append(row_dic.get('create_time'))
            tb.add_row(show_row)
        tb.align['func'] = 'l'
        print(tb)

    @staticmethod
    def _type_str(thing):
        _type = re.findall('\'([^\']+)\'', str(type(thing)))[0]


if __name__ == "__main__":
    S = Sxclzy()

    # S.count_down('08-19', 'm-d')


    class A:
        def test_a(self, name):
            print('Hi {}! test is running'.format(name))
            self.test_b(name)

        def test_b(self, name):
            print('call from test_a: ', 'hi {}'.format(name))


    def test(name):
        print('Hi {}! '.format(name))


    S.add_schedule(name='func1',
                   func=test,
                   schedule={'S': '*/10'},
                   run_times=3,
                   args={'name': 'Lilei'},
                   status=1,
                   overwrite_if_exist=True
                   )
    # get_res = S.get_schedules(print_pretty=True)
    # print(get_res)
    # S.clear_schedules()
    S.start()
