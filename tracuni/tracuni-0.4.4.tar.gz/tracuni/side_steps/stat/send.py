import aiozipkin.transport as azt
import logging
from urllib.parse import quote

from tracuni.side_steps.stat.adapter import StatsD
from tracuni.misc.select_coroutine import get_coroutine_decorator
from tracuni.define.const import STATSD_DURATION_FACTOR
async_decorator = get_coroutine_decorator()


class TracerTransport(azt.Transport):
    # noinspection PyProtectedMember
    def __init__(
            self,
            logging_conf,
            statsd_conf,
            loop,
            use_tornado=False,
    ):
        tracer_url = logging_conf.url
        send_interval = logging_conf.send_interval
        super(TracerTransport, self).__init__(
            tracer_url,
            send_interval=send_interval,
            loop=loop
        )
        self.loop = loop
        self.__tracer = logging_conf.name
        self.use_tornado = use_tornado

        statsd_conf = StatsD.read_statsd_configuration(statsd_conf)
        self.stats = None
        if statsd_conf.enable:
            self.stats = StatsD(statsd_conf._asdict())
            self.stats.connect()
        else:
            logging.warning("StatsD send has NOT been started")
        self.statsd_is_configured = statsd_conf.enable and self.stats
        if self.statsd_is_configured:
            logging.info("StatsD send is nominal")

    @async_decorator
    def _send(self):
        data = self._queue[:]

        try:
            if self.statsd_is_configured:
                yield self._send_to_statsd(data)
        except Exception as e:
            logging.exception(e)

        try:
            if self.__tracer == 'zipkin':
                if self.use_tornado:
                    yield super(TracerTransport, self)._send()
                else:
                    yield from super(TracerTransport, self)._send()
            else:
                self._queue = []
        except Exception as e:
            logging.exception(e)

    @async_decorator
    def _send_to_statsd(self, data):
        if self.stats:
            for rec in data:
                name = rec['name']
                tags = rec.get('tags', {})

                api_kind = name.split('::')[0]
                span_side = rec['kind']
                json_method = tags.get('data.method')
                json_response_code = str(tags.get('data.code'))
                widget_id = tags.get('app.widget')
                app_method = tags.get('app.method', '').split(':')[-1]
                rq_hostname = tags.get('rq.url.hostname')
                try:
                    rsp_status = int(tags.get('rsp.status') or 0)
                except ValueError:
                    rsp_status = 0
                duration = int(round(rec["duration"] / STATSD_DURATION_FACTOR))

                span_side_map = {
                    'SERVER': 'in',
                    'CLIENT': 'out',
                }

                if tags.get('error') is not None:
                    own = tags.get('error.own')
                    xls = tags.get('error.class')

                    if own or api_kind == '<unknown>':
                        variant = "tracer_own"
                    else:
                        variant = f"{api_kind}_{span_side_map.get(span_side)}"

                    # ALL:ALL if error
                    # counter <unit_name>.exception,class=x,variant=x
                    # class = exception class name
                    # variant = ((HTTP|AMQP|DB_IN|OUT)|tracer_own)
                    self.stats.exception_count_glork(xls, variant)

                if api_kind == 'http':
                    if span_side == 'CLIENT':
                        # HTTP:OUT
                        # timer <unit_name>.http_requests,code=x,hostname=x
                        # code = peer http response code
                        # hostname = peer address
                        self.stats.http_out_time_glork(
                            rsp_status, rq_hostname,
                            duration
                        )
                    elif span_side == 'SERVER':
                        # HTTP:IN
                        # counter <unit_name>.gen_response_code,code=x,widget_id=x,method=x
                        # code = API response code, where 0 = success
                        # widget_id = widget data from request
                        # method = API method from request
                        if json_response_code is not None:
                            self.stats.http_in_code_count_glork(
                                json_response_code, widget_id, json_method
                            )
                        # HTTP:IN
                        # timer <unit_name>.handler_timers,name=x,widget_id=x,method=x
                        # name = handler method name
                        # widget_id = widget data from request
                        # method = API method from request
                        self.stats.http_in_method_time_glork(
                            app_method, widget_id, json_method,
                            duration,
                        )

                if api_kind == 'db':
                    # DB:OUT
                    # timer <unit_name>.db_query_function,func_name=<method_name>
                    # func_name = db api method name
                    self.stats.db_time_glork(
                        app_method,
                        duration,
                    )
