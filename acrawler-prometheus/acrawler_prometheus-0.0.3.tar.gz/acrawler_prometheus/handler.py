from acrawler import Handler, get_logger
from prometheus_client import start_http_server, Histogram, Counter, Gauge
import asyncio

logger = get_logger("prometheus")


class PromExporter(Handler):
    family = "Task"
    priority = 100

    async def on_start(self):
        self.name = self.crawler.name
        self.port = self.crawler.config.get("PROMETHEUS_PORT", 8000)
        self.addr = self.crawler.config.get("PROMETHEUS_ADDR", "localhost")
        self.interval = self.crawler.config.get("PROMETHEUS_INTERVAL", 1)

        self.reqs = Gauge(
            f"{self.name}_requests_progress", "Number of working requests"
        )
        self.reqs_q = Gauge(
            f"{self.name}_requests_queue", "Number of requests in ready queue"
        )
        self.reqs_w = Gauge(
            f"{self.name}_requests_waiting", "Number of requests in waiting queue"
        )

        self.counts = {}

        self.crawler.create_task(self.start_server())
        self.crawler.create_task(self.export())

    async def start_server(self):
        logger.info(
            f"Set up prometheus exporter http server at http://{self.addr}:{self.port} ..."
        )
        start_http_server(self.port, self.addr)

    async def export(self):
        await asyncio.sleep(1)
        while 1:
            await self.log()
            await asyncio.sleep(self.interval)

    async def log(self):
        required = await self.crawler.counter.get_required()
        if required:
            self.reqs.set(required)

        self.reqs_q.set(await self.crawler.sdl_req.q.get_length_of_pq())
        self.reqs_w.set(await self.crawler.sdl_req.q.get_length_of_waiting())

        counts_dict = await self.crawler.counter.get_counts_dict()
        for family in counts_dict.keys():
            success = counts_dict[family][1]
            failure = counts_dict[family][0]

            if family not in self.counts:
                self.counts[family] = self.get_default_gauges(family)
            gauge_s, gauge_f = self.counts[family]
            gauge_s.set(success)
            gauge_f.set(failure)

    def get_default_gauges(self, family):
        return (
            Gauge(f"{self.name}_{family}_success", f"Number of successful {family}."),
            Gauge(f"{self.name}_{family}_failure", f"Number of failed {family}."),
        )
