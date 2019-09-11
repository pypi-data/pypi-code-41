# https://pendulum.eustace.io/docs/#addition-and-subtraction

import pendulum


def parse(time_str: str, tz='Asia/Shanghai'):
    """
    format '2019-08-01 00:00:00.000' to pendulum
    :param time_str: 时间格式字符串
    :param tz: 时区
    :return: pendulum
    """
    return pendulum.parse(time_str, tz=tz)


def get_local_time(dt):
    """
    输出本地时间格式
    :param dt: pendulum parse 对象
    :return: 按照'YYYY-MM-DD HH:mm:ss.SSS'format后的字符串
    """
    return dt.format('YYYY-MM-DD HH:mm:ss.SSS')


def get_cloud_time(dt):
    """
    输出云端时间格式
    :param dt: pendulum parse 对象
    :return: 纳秒级
    """
    return int(dt.timestamp() * 1000000000)


def get_dt_duration_seconds(dt1, dt2):
    """
    计算pendulum parse 对象的秒级差
    :param dt1:
    :param dt2:
    :return:
    """
    return (dt1 - dt2).seconds


def now():
    return int(pendulum.now(tz='Asia/Shanghai').timestamp() * 1000)


if __name__ == '__main__':
    t_time_str = '2019-08-01 00:00:00.000'
    t_dt = parse(t_time_str)

    print(t_dt)
    print(get_local_time(t_dt))
    print(get_cloud_time(t_dt))

    t_time_str2 = '2019-08-01 00:00:05.000'
    t_dt2 = parse(t_time_str2)

    print(get_dt_duration_seconds(t_dt2, t_dt))

    print(t_dt2 > t_dt)

    print(now())
