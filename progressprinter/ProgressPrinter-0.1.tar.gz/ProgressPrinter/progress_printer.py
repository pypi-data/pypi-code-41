import sys


class ProgressPrinter:
    def __init__(self, units, unit_type='', length=50, pre='', post='', fill='=', head='>', empty=' '):

        self.steps = length / units
        self.length = length
        self.units = units
        self.unit_type = unit_type
        self.pre = pre
        self.post = post
        self.fill = fill
        self.head = head
        self.empty = empty
        self.float_flag = False

    def print_progress(self, current_unit=0, pre=''):
        if type(self.units) == float or type(current_unit) == float or self.float_flag:
            self.float_flag = True
            info_text = '] - Finished {:.2f} {} of {:.2f} {}     '.format(float(current_unit), self.unit_type,
                                                                          float(self.units), self.unit_type)
        else:
            info_text = '] - Finished {} {} of {} {}     '.format(current_unit, self.unit_type, self.units,
                                                                  self.unit_type)
        if self.head != '' and current_unit != 0:
            progress = self.fill * (round(current_unit * self.steps) - 1) + self.head
        else:
            progress = self.fill * round(current_unit * self.steps)
        empty = self.empty * (self.length - len(progress))
        if current_unit == 0:
            if self.pre != '':
                sys.stdout.write('\n' + self.pre + '\n')
            if pre != '':
                sys.stdout.write(pre + '\n')
            sys.stdout.write('[' + progress + empty + info_text)
        else:
            if pre != '':
                sys.stdout.write('\r' + pre + ' ' * (self.length + len(info_text) - len(pre)) + '\n')
                sys.stdout.write('[' + progress + empty + info_text)
            else:
                sys.stdout.write('\r[' + progress + empty + info_text)
        if current_unit == self.units:
            sys.stdout.write('\n')
            if self.post != '':
                sys.stdout.write(self.post + '\n\n')
            self.float_flag = False
        sys.stdout.flush()
