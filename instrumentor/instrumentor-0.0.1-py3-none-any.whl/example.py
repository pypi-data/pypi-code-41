from instrumentor.registry import CollectorRegistry
from instrumentor.metrics import Counter

from redis import Redis

redis = Redis()

reg = CollectorRegistry(redis_client=redis, namespace="test")

http_request_total = Counter(name="http_request_total", description="Test")

reg.register(http_request_total)

http_request_total.inc()
