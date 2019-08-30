from .metric_base import MetricBase

class CarbonStatsdBase(MetricBase):

    def __init__(self, host='localhost', port=8125, environment="dev", app_name="myapp"):
        super(CarbonStatsd, self).__init__(host, port, environment)
        self.measurement = 'generic.carbon.statsd.%s.%s' %(
            self.environment, app_name
        )

        try:
            self.connection = self.connect()
        except Exception as e:
            print("Unable to initalise metrics client: %s" % e)


class TimerCounter(CarbonStatsdBase):
    """
    Decorate any method to post a metric and timer

    Example:

        @TimerCounter(stat="post", module_name=__init__)
        def post():
            pass
    """
    def __call__(self, fn):

        @wraps(fn)
        def decorated(*args, **kwargs):
            stat = self.concat_stat_name(
                self.get_module_name(self.module_name),
                self.get_stat_name(self.stat)
            )
            statsd.incr("%s.count" % stat)
            with statsd.timer(stat="%s.time" % stat):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    statsd.incr("%s.error" % stat)
                    statsd.incr("%s.error.%s" % (stat, exc_type.__name__))
                    raise
        return decorated


class FirstArgTimerCounter(BaseTimerCounterDecorator):
    """
    Decorate a method that has an SQLAlchemy model or record as it's
    first arguement to submit  a counter and a timer.

    Example:

        @FirstArgTimerCounter(stat="push_to_sns", module_name=__init__)
        def push_to_sns(topic_name):
            pass
    """

    def __call__(self, fn):

        @wraps(fn)
        def decorated(*args, **kwargs):
            stat = self.concat_stat_name(
                self.get_module_name(self.module_name),
                self.get_stat_name(self.stat)
            )
            arg_name_stat = "%s.%s" % (stat, str(args[1]))
            statsd.incr("%s.count" % stat)
            statsd.incr("%s.count" % arg_name_stat)
            with statsd.timer(stat="%s.time" % stat):
                with statsd.timer(stat="%s.time" % arg_name_stat):
                    try:
                        return fn(*args, **kwargs)
                    except Exception:  # pragma: no cover
                        statsd.incr("%s.error" % stat)
                        statsd.incr("%s.error" % arg_name_stat)
                        raise
        return decorated

