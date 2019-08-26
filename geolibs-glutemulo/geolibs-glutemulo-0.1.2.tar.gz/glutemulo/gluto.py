import sys

from glutemulo.config import config
from glutemulo.kafka.consumer import JsonKafka as Consumer
from glutemulo.kafka.producer import JsonKafka as Producer
from glutemulo.logger import log

if config["backend"] == "carto":
    from glutemulo.backend.carto import CartoBackend as Backend

    log.debug("Using CARTO backend")
elif config["backend"] == "postgres":
    from glutemulo.backend.postgres import PostgresBackend as Backend

    log.debug("Using POSTGRES backend")
elif config["backend"] == "redis":
    from glutemulo.backend.redis import RedisBackend

    log.debug("Using REDIS backend")
else:
    from glutemulo.backend.logger import LoggerBackend as Backend

    log.debug("Using LOGGER backend")


if __name__ == "__main__":
    if not config["ingestor_enabled"]:
        log.error("Disabled. Please set GLUTEMULO_INGESTOR_ENABLED")
        sys.exit(1)
    if not config["ingestor_topic"]:
        log.error("No topic found. Please set GLUTEMULO_INGESTION_TOPIC")
        sys.exit(1)

    consumer = Consumer(
        config["ingestor_topic"],
        bootstrap_servers=config["ingestor_bootstap_servers"],
        group_id=config["ingestor_group_id"],
        auto_offset_reset=config["ingestor_auto_offset_reset"],
        max_poll_records=config["ingestor_max_poll_records"],
        fetch_min_bytes=config["ingestor_fetch_min_bytes"],
    )

    if config["backend"] == "redis":
        backend = RedisBackend(
            config["redis_expire_seconds"],
            config["redis_key_prefix"],
            **config["redis_connection"],
        )
    else:

        backend = Backend(
            config["ingestor_dataset"],
            config["ingestor_dataset_columns"],
            config["ingestor_dataset_ddl"],
            config["ingestor_dataset_autocreate"],
        )
    while True:
        for messages in consumer.consume(config["ingestor_wait_interval"]):
            if messages:
                backend.consume(messages)
