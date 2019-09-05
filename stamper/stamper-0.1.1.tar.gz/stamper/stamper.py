
import json
import os.path
from datetime import datetime, timedelta
from os import symlink, remove, makedirs
from collections import OrderedDict
from operator import itemgetter
import pygal

from .http import HTTPClient
from .config import Config
from .filters import DateFilter


class Stamper(object):

    def __init__(self, config_file=None):
        self.config = Config(config_file)
        self.stamps_file = os.path.expanduser(
            self.config.get('stamps', 'path'))
        self.charts_dir = os.path.expanduser(
            self.config.get('charts', 'path'))
        self.date_format = self.config.get('stamps', 'date_format')
        self.time_format = self.config.get('stamps', 'time_format')
        self.datetime_format = self.config.get('stamps', 'datetime_format')
        self.wants_seconds = self.config.get('stamps', 'wants_seconds')
        self.hours_day = int(self.config.get('sum', 'hours_day'))
        self.collector = self.config.get('collector')
        self.ensure_stamps_file()
        self.ensure_charts_dir()
        self.stamps = []
        self.date_filter = DateFilter(self.date_format)

    def __json_load(self, filename):
        """
        Load the stamps from a file in json format, returning
        the parsed list.
        """
        with open(filename, 'r') as stamps_file:
            try:
                stamps = json.load(stamps_file)
            except ValueError:
                stamps = []
        return stamps

    def remove_duplicates(self):
        """
        Remove duplicated stamps from the stamps list
        """
        stamps = [dict(t) for t in set(
            [tuple(d.items()) for d in self.stamps])]
        self.stamps = stamps

    def ensure_stamps_file(self):
        if not os.path.exists(self.stamps_file):
            with open(self.stamps_file, 'w') as stamps_file:
                stamps_file.write('')

    def ensure_charts_dir(self):
        if not os.path.exists(self.charts_dir):
            makedirs(self.charts_dir)

    def load_stamps(self):
        self.stamps = self.__json_load(self.stamps_file)

    def sort_stamps(self):
        """
        Sort all the stamps by start and end dates
        """
        self.stamps = sorted(self.stamps, key=itemgetter('start', 'end'))

    def save_stamps(self):
        with open(self.stamps_file, 'w') as stamps_file:
            json.dump(self.stamps, stamps_file, indent=4)

    def stamp(self, start, end, customer, action):
        self.stamps.append({
            'start': start,
            'end': end,
            'customer': customer,
            'action': action,
        })

    def last_stamp(self, n=1):
        """
        return the stamp in position -n, that is, starting from the latest one
        and going back N positions in the list of stamps
        """
        if not self.stamps:
            return None
        return self.stamps[-n]

    def worktime(self, start, end):
        worktime = (datetime.strptime(end, self.datetime_format) -
                    datetime.strptime(start, self.datetime_format))
        return worktime.seconds

    @property
    def customers(self):
        customers = []
        for stamp in self.stamps:
            if stamp['customer'] not in customers:
                customers.append(stamp['customer'])
        customers.remove(None)
        return customers

    def totals(self, filter_from=None, filter_to=None, filter_descr=None):
        totals = {}
        for stamp in self.stamps:
            customer = stamp['customer']
            # customer will be None for "start" stamps, having no end time
            if customer:
                start = datetime.strptime(stamp['start'], self.datetime_format)
                end = datetime.strptime(stamp['end'], self.datetime_format)
                if filter_from and start < filter_from:
                    # if there is a filter setting a starting date for the
                    # report and the current stamp is from an earlier date, do
                    # not add it to the totals
                    continue
                if filter_to and start > filter_to:
                    # similar for the end date
                    continue
                if filter_descr and filter_descr not in stamp['action']:
                    continue
                if customer not in totals:
                    totals[customer] = 0
                totals[customer] += self.worktime(stamp['start'], stamp['end'])
        return totals

    def details(self, filter_customer=None, filter_from=None, filter_to=None,
                filter_descr=None):
        details = OrderedDict()
        totals = OrderedDict()
        total_customer = OrderedDict()
        for stamp in self.stamps:
            customer = stamp['customer']
            if customer:
                if filter_customer and customer != filter_customer:
                    # we are getting the details for only one customer, if this
                    # stamp is not for that customer, simply move on and ignore
                    # it
                    continue
                start = datetime.strptime(stamp['start'], self.datetime_format)
                start_day = start.strftime('%Y-%m-%d')
                end = datetime.strptime(stamp['end'], self.datetime_format)
                if filter_from and start < filter_from:
                    # if there is a filter setting a starting date for the
                    # report and the current stamp is from an earlier date, do
                    # not add it to the totals
                    continue
                if filter_to and start > filter_to:
                    # similar for the end date
                    continue
                if filter_descr and filter_descr not in stamp['action']:
                    continue
                # avoid "start" stamps
                if start_day not in details:
                    details[start_day] = []
                if start_day not in totals:
                    totals[start_day] = 0
                worktime = self.worktime(stamp['start'], stamp['end'])
                str_worktime = str(timedelta(seconds=worktime))
                if not self.wants_seconds or self.wants_seconds == 'false':
                    # remove the seconds part from the string representation
                    str_worktime = ':'.join(str_worktime.split(':')[:-1])
                details[start_day].append(
                    '%(worktime)s %(customer)s %(action)s' % {
                        'worktime': str_worktime,
                        'customer': customer,
                        'action': stamp['action']
                    })
                totals[start_day] += worktime
                if start_day not in total_customer:
                    total_customer[start_day] = {}
                if customer not in total_customer[start_day]:
                    total_customer[start_day][customer] = 0
                total_customer[start_day][customer] += worktime
        for day in totals:
            totals[day] = str(timedelta(seconds=totals[day]))
            if not self.wants_seconds or self.wants_seconds == 'false':
                # remove the seconds part from the string representation
                totals[day] = ':'.join(totals[day].split(':')[:-1])
        return details, totals, total_customer

    def timeline(self, customer=None, stamp_filter=None, filter_descr=None):
        filter_from, filter_to = self.date_filter.validate(stamp_filter)
        for stamp in self.stamps:
            start = datetime.strptime(stamp['start'], self.datetime_format)
            start_day = start.strftime('%Y-%m-%d')
            if filter_from and start < filter_from:
                # if there is a filter setting a starting date for the
                # report and the current stamp is from an earlier date, do
                # not add it to the totals
                continue
            if filter_to and start > filter_to:
                # similar for the end date
                continue
            if filter_descr and stamp['action']:
                if filter_descr not in stamp['action']:
                    continue
            if not stamp['customer']:
                if customer is None:
                    print(stamp['start'] + ' start')
            else:
                if customer and customer != stamp['customer']:
                    continue
                if customer:
                    print(stamp['start'] + ' start')
                print(' '.join([stamp['end'],
                                stamp['customer'],
                                stamp['action']]))

    def graph_stamps(self, customer=None, stamp_filter=None, filter_descr=None):
        """
        Generate charts with information from the stamps
        """
        filter_from, filter_to = self.date_filter.validate(stamp_filter)
        chart = pygal.Bar(title='Work hours per day',
                          range=(0, self.hours_day),
                          x_title='Days',
                          y_title='Work hours',
                          x_label_rotation=45)

        details, totals, totals_customers = self.details(customer,
                                                         filter_from,
                                                         filter_to,
                                                         filter_descr)
        days = []
        values = {}
        for c in self.customers:
            values[c] = []

        found = []

        for day in details:
            for c in values:
                seconds = totals_customers[day].get(c, 0)
                if seconds and c not in found:
                    found.append(c)
                human = timedelta(seconds=seconds).__str__()
                values[c].append({'value': seconds/60.00/60.00,
                                  'label': day + ': ' + human})
            days.append(day)
        chart.x_labels = map(str, days)

        if customer:
            chart.add(customer, values[customer])
        else:
            for c in found:
                chart.add(c, values[c])

        chart_name = 'chart-%s.svg' % datetime.today().strftime(
            '%Y-%m-%d_%H%M%S')
        chart_symlink = 'chart-latest.svg'
        chart_path = os.path.join(self.charts_dir, chart_name)
        chart_symlink_path = os.path.join(self.charts_dir, chart_symlink)

        chart.render_to_file(chart_path)
        print('Rendered chart: ' + chart_path)
        if os.path.islink(chart_symlink_path):
            remove(chart_symlink_path)
        symlink(chart_name, chart_symlink_path)
        print('Updated latest chart: ' + chart_symlink_path)

    def show_stamps(self, customer=None, stamp_filter=None, verbose=False,
        sum=False, filter_descr=None):
        filter_from, filter_to = self.date_filter.validate(stamp_filter)

        # If the user asks for verbose information, show it before the
        # totals (mimicing what the original stamp tool does)
        if verbose:
            details, totals, total_customer = self.details(customer,
                                                           filter_from,
                                                           filter_to,
                                                           filter_descr)
            for day in details:
                print('------ %(day)s ------' % {'day': day})
                for line in details[day]:
                    print(line)
                customer_day_totals = []
                for tc in total_customer[day]:
                    tc_total = str(timedelta(seconds=total_customer[day][tc]))
                    if not self.wants_seconds or self.wants_seconds == 'false':
                        # remove the seconds part from the string representation
                        tc_total = ':'.join(tc_total.split(':')[:-1])
                        # ensure hours show double digits
                        tc_total = tc_total.zfill(5)
                    customer_day_totals.append(tc+': '+tc_total)
                print(', '.join(customer_day_totals))
                if len(customer_day_totals) > 1:
                    # if there are multiple customers in the report, show the
                    # daily totals
                    print('daily total: %(total)s' % {'total': totals[day]})
            print('-'*79)

        # now calculate the totals and show them
        totals = self.totals(filter_from, filter_to, filter_descr)
        if customer:
            seconds=totals.get(customer, 0)
            total = timedelta(seconds=totals.get(customer, 0))
            if not self.wants_seconds or self.wants_seconds == 'false':
                # remove the seconds part from the string representation
                total = ':'.join(str(total).split(':')[:-1])
            print(' %(customer)s: %(total)s' % {'customer': customer,
                                                'total': total})
        else:
            for c in totals:
                seconds=totals[c]
                total = timedelta(seconds=totals[c])
                if not self.wants_seconds or self.wants_seconds == 'false':
                    # remove the seconds part from the string representation
                    total = ':'.join(str(total).split(':')[:-1])
                print(' %(customer)s: %(total)s' % {'customer': c,
                                                    'total': total})

        if sum:
            sum_tot = ''
            if totals:
                print('------ Totals ------' % {'day': day})
                for day, tot in totals.items():
                    print(' %(day)s: %(total)s' % {'day': day, 'total': tot})
                    sum_tot = "%(total)s %(new)s" % {
                        'total': sum_tot,
                        'new': total
                    }
                totalSecs, sec = divmod(seconds, 60)
                hr, min = divmod(totalSecs, 60)
                totalDays, remaining = divmod(seconds,
                                              (self.hours_day * 60 * 60))
                remainingMin, remainingSec = divmod(remaining, (60))
                remainingHr, remainingMin = divmod(remainingMin, (60))
                print('----- %d:%02d:%02d -----' % (hr, min, sec))
                print('--- %d days, remaining: %d:%02d (%d hours/day) ---' % (
                    totalDays, remainingHr, remainingMin, self.hours_day
                ))

    def remove_stamps(self, n=1):
        """
        Remove up to n stamps back, asking for confirmation before delete
        """
        for i in range(n):
            stamp = self.last_stamp()
            if not stamp['customer']:
                print(stamp['start'] + ' start')
            else:
                print(' '.join([stamp['end'],
                                stamp['customer'],
                                stamp['action']]))
            confirm = ''
            while confirm.lower() not in ['y', 'n']:
                confirm = raw_input('delete stamp? (y/n) ')
                confirm = confirm.lower()
            if confirm == 'y':
                self.stamps.pop()
            else:
                # if the user says no to the removal of an stamp, we cannot
                # keep deleting stamps after that one, as that could leave the
                # stamps in an inconsistent state.
                print('Aborting removal of stamps')
                break
        self.save_stamps()

    def import_stamps(self, filename):
        """
        Import the stamps from the given file into the main stamps list,
        merging them into the list (removing duplicated entries)
        """
        if not os.path.exists(filename):
            print('[error] ' + filename + 'does not exist')
            return
        if os.path.isdir(filename):
            print('[error] ' + filename + 'is a directory')
            return
        stamps = self.__json_load(filename)
        if not stamps:
            print('[warning] no stamps can be imported from ' + filename)
            return
        self.stamps.extend(stamps)
        self.remove_duplicates()
        self.sort_stamps()
        self.save_stamps()
        print('[warning] ' + str(len(stamps)) + ' stamps merged')
        print('[warning] remember to review the resulting stamps file')

    def push_stamps(self, customer=None, stamp_filter=None, filter_descr=None):
        filter_from, filter_to = self.date_filter.validate(stamp_filter)

        stamps = []
        for stamp in self.stamps:
            if stamp['customer']:
                if customer and customer != stamp['customer']:
                    continue
                start = datetime.strptime(stamp['start'], self.datetime_format)
                start_day = start.strftime('%Y-%m-%d')
                end = datetime.strptime(stamp['end'], self.datetime_format)
                if filter_from and start < filter_from:
                    # if there is a filter setting a starting date for the
                    # report and the current stamp is from an earlier date, do
                    # not add it to the totals
                    continue
                if filter_to and start > filter_to:
                    # similar for the end date
                    continue
                if filter_descr and filter_descr not in stamp['action']:
                    continue
                stamps.append(stamp)

        stamps = json.dumps(stamps, indent=4)
        http_client = HTTPClient(self.collector['base_url'])
        response = http_client.post(self.collector['login_path'],
                                    {'username': self.collector['user'],
                                    'password': self.collector['password']})
        # response is a json-encoded list of end-points from the collector api
        try:
            api = json.loads(response)
        except ValueError:
            print('[error] No valid api end points can be retrieved')
            return

        response = http_client.post(api['push'], {'stamps': stamps})

        # response is a json-encoded dict, containing lists of added, updated
        # and deleted stamps (on the other side)
        try:
            results = json.loads(response)
        except ValueError:
            print('[error] stamps pushed, can not retrieve results information')
            return

        # display information
        for k in results.keys():
            print('%(stamps)d stamps %(action)s' % {'stamps': len(results[k]),
                                                    'action': k})
