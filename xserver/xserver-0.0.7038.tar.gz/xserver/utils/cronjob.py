#coding: utf8
from __future__ import absolute_import
from crontab import CronTab
from xserver.utils import string_types


# job  = cron.new(command='/usr/bin/echo')
#job.minute.during(5,50).every(5)
#job.hour.every(4)
#job.day.on(4, 5, 6)

#job.dow.on('SUN')
#job.dow.on('SUN', 'FRI')
#job.month.during('APR', 'NOV')

# job.setall('2 10 * * *')


def get_cronjob_by_command(command, user='root', on_reboot=False):
    cron = CronTab(user)
    command = command.strip()
    jobs = list(cron.find_command(command))
    if on_reboot:
        jobs = [job for job in jobs if '@reboot' in str(job)]
    if not jobs:
        return
    else:
        return jobs[0]



def reset_cron_lines(cron):
    cron_lines = []
    if cron.lines:
        for line in cron.lines:
            if not isinstance(line, string_types):
                cron_lines.append(line)
    cron_lines_copy = list(cron.lines)
    for line in cron_lines_copy:
        try: cron.lines.remove(line)
        except: pass
    for line in cron_lines:
        cron.lines.append(line)


def create_cronjob(command, user='root', minutes=None, hours=None, write=False, on_reboot=False, minute_at=0,):
    cron = CronTab(user)

    cron_items_to_remove = []
    for cron_item in cron.crons:
        if cron_item.command == command:
            cron_items_to_remove.append(cron_item)
    for cron_item in cron_items_to_remove:
        cron.remove(cron_item)

    job = cron.new(command)

    if on_reboot:
        job.every_reboot()
    else:
        if minutes:
            if minutes >= 60:
                minutes = 59
            job.minute.every(minutes)
        if hours:
            job.hour.every(hours)
            job.minute.on(minute_at)
    if write:
        reset_cron_lines(cron)
        cron.write()

    return job


def create_py_command_cronjob(py_command, user='root', minutes=None, on_reboot=False, write=False):
    command = 'python -c "%s"' % py_command
    return create_cronjob(command, user=user, minutes=minutes, on_reboot=on_reboot, write=write)

