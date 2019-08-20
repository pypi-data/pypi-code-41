from django.db import models

class MonthsAdd(models.Func):
    """
    Custom Func expression to add date and int fields as day addition
    """
    function = 'DATE_ADD'
    arg_joiner = ", INTERVAL "
    template = "%(function)s(%(expressions)s MONTH)"
    output_field = models.DateTimeField()


class DaysAdd(models.Func):
    """
    Custom Func expression to add date and int fields as day addition
    """
    function = 'DATE_ADD'
    arg_joiner = ", INTERVAL "
    template = "%(function)s(%(expressions)s DAY)"
    output_field = models.DateTimeField()